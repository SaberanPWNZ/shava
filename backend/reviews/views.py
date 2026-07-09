import logging

from django.db.models import Count, Prefetch, Q, QuerySet
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import permissions, status, views, viewsets
from rest_framework import serializers as drf_serializers
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.generics import ListAPIView, ListCreateAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from notifications.services import notify
from places.models import ModerationLog, Place
from reviews.models import Review, ReviewHelpfulVote, ReviewReply
from reviews.serializers import (
    ReviewCreateSerializer,
    ReviewReplySerializer,
    ReviewSerializer,
)

logger = logging.getLogger("reviews")


def with_viewer_votes_prefetch(qs: QuerySet, request) -> QuerySet:
    """Annotate ``qs`` so each ``Review`` exposes a ``viewer_votes`` list
    containing only the helpful-vote rows belonging to the current user.

    The prefetch is intentionally narrow (filtered by ``user_id``) so the
    ``ReviewSerializer.get_viewer_voted`` lookup is O(1) per row instead of
    issuing a query each. For anonymous requests we skip the prefetch — the
    serializer short-circuits to ``False`` without touching the DB.
    """

    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_authenticated", False):
        return qs
    return qs.prefetch_related(
        Prefetch(
            "helpful_votes",
            queryset=ReviewHelpfulVote.objects.filter(user_id=user.id),
            to_attr="viewer_votes",
        )
    )


def with_replies_count(qs: QuerySet) -> QuerySet:
    """Annotate the visible-replies count so lists stay N+1-free."""
    return qs.annotate(
        _replies_count=Count(
            "replies", filter=Q(replies__is_deleted=False), distinct=True
        )
    )


REVIEW_ORDERING = {
    # "newest" is the model default; "helpful" surfaces community-endorsed
    # reviews; "top"/"low" let visitors jump straight to raves or warnings.
    "newest": "-created_at",
    "oldest": "created_at",
    "helpful": "-helpful_count",
    "top": "-score",
    "low": "score",
}


def apply_review_list_params(qs: QuerySet, params) -> QuerySet:
    """Apply the shared ``ordering`` / ``with_photos`` query params."""
    if str(params.get("with_photos", "")).lower() in ("1", "true", "yes"):
        qs = qs.filter(dish_image__gt="")
    order = REVIEW_ORDERING.get(params.get("ordering") or "newest")
    if order:
        # Stable tie-break so pagination never shows duplicates.
        qs = qs.order_by(order, "-id")
    return qs


@extend_schema(tags=["reviews"])
class ReviewViewSet(viewsets.ModelViewSet):
    """A user's own reviews."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # `place` and `author` are both rendered by the serializer →
        # join them in a single query to avoid N+1 on /reviews/.
        qs = Review.objects.filter(
            author=self.request.user, is_deleted=False
        ).select_related("place", "author")
        return with_replies_count(with_viewer_votes_prefetch(qs, self.request))

    def get_serializer_class(self):
        if self.action == "create":
            return ReviewCreateSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        instance = serializer.save(author=self.request.user, is_moderated=False)
        logger.info(
            "Review created (pending moderation): %s for %s by %s",
            instance.score,
            instance.place.name,
            self.request.user,
        )

    def perform_update(self, serializer):
        # An edited review goes back to the moderation queue: otherwise an
        # author could get an innocuous text approved and then swap it for
        # spam/abuse that keeps the "approved" flag.
        instance = serializer.save(is_moderated=False)
        if instance.place_id:
            instance.place.recalculate_rating_from_reviews()

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])
        # Recompute the place rating in case the deleted review was approved.
        if instance.place_id:
            instance.place.recalculate_rating_from_reviews()


@extend_schema(
    tags=["reviews"],
    parameters=[
        OpenApiParameter(
            "ordering",
            str,
            OpenApiParameter.QUERY,
            required=False,
            enum=sorted(REVIEW_ORDERING),
            description="Sort order; defaults to newest.",
        ),
        OpenApiParameter(
            "with_photos",
            bool,
            OpenApiParameter.QUERY,
            required=False,
            description="Only reviews that include a dish photo.",
        ),
    ],
)
class PlaceReviewsListCreateView(ListCreateAPIView):
    """List approved reviews for a place; create a new (pending) review."""

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        place_id = self.kwargs.get("place_pk") or self.kwargs.get("place_id")
        # `author` is rendered via `author_username`; `place` via
        # `place_name`. Pull both in a single JOIN to avoid N+1.
        qs = Review.objects.filter(place_id=place_id, is_deleted=False).select_related(
            "author", "place"
        )
        qs = with_replies_count(with_viewer_votes_prefetch(qs, self.request))
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return apply_review_list_params(qs, self.request.query_params)
        # Authors see their own pending reviews + everyone's approved reviews.
        if user.is_authenticated:
            qs = qs.filter(Q(is_moderated=True) | Q(author=user))
        else:
            qs = qs.filter(is_moderated=True)
        return apply_review_list_params(qs, self.request.query_params)

    def perform_create(self, serializer):
        place_id = self.kwargs.get("place_pk") or self.kwargs.get("place_id")
        place = get_object_or_404(Place, pk=place_id)
        if Review.objects.filter(
            author=self.request.user, place=place, is_deleted=False
        ).exists():
            raise DRFValidationError("You have already reviewed this place.")
        serializer.save(author=self.request.user, place=place, is_moderated=False)


# Backwards-compatible alias used elsewhere.
class PlaceReviewsListView(PlaceReviewsListCreateView):
    pass


@extend_schema(
    tags=["reviews"],
    summary="Public feed of the latest approved reviews",
    parameters=[
        OpenApiParameter(
            "city",
            str,
            OpenApiParameter.QUERY,
            required=False,
            description="Filter by place city (name, slug or city id).",
        ),
    ],
)
class ReviewFeedView(ListAPIView):
    """Site-wide "what's happening" feed: newest approved reviews.

    Public and cheap on purpose — it powers the landing page, so it must
    render for anonymous visitors and stay at a constant query count.
    """

    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Review.objects.filter(is_moderated=True, is_deleted=False).select_related(
            "author", "place"
        )
        city = self.request.query_params.get("city")
        if city:
            cond = Q(place__city__iexact=city) | Q(place__city_ref__slug__iexact=city)
            if str(city).isdigit():
                cond |= Q(place__city_ref_id=int(city))
            qs = qs.filter(cond)
        qs = with_replies_count(with_viewer_votes_prefetch(qs, self.request))
        return qs.order_by("-created_at", "-id")


@extend_schema(tags=["reviews"], summary="Public list of a user's approved reviews")
class UserReviewsListView(ListAPIView):
    """Approved reviews written by one user — powers the public profile page.

    Banned/deactivated authors 404 just like their profile does, so content
    disappears together with the account.
    """

    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        from django.contrib.auth import get_user_model

        author = get_object_or_404(
            get_user_model(),
            pk=self.kwargs["user_pk"],
            is_active=True,
            is_banned=False,
        )
        qs = Review.objects.filter(
            author=author, is_moderated=True, is_deleted=False
        ).select_related("author", "place")
        qs = with_replies_count(with_viewer_votes_prefetch(qs, self.request))
        return qs.order_by("-created_at", "-id")


@extend_schema(tags=["reviews"])
class ReviewRepliesListCreateView(ListCreateAPIView):
    """List replies under a review; post a new reply (authenticated).

    Replies inherit the review's visibility: anyone can read replies to an
    approved review; a pending review's replies are only reachable by its
    author or staff (matching the review itself).
    """

    serializer_class = ReviewReplySerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_throttles(self):
        if self.request.method == "POST":
            self.throttle_scope = "reply"
        return super().get_throttles()

    def _get_review(self):
        review = get_object_or_404(Review, pk=self.kwargs["pk"], is_deleted=False)
        user = self.request.user
        if not review.is_moderated:
            is_privileged = user.is_authenticated and (
                user.is_staff or review.author_id == user.id
            )
            if not is_privileged:
                from django.http import Http404

                raise Http404("Review not found.")
        return review

    def get_queryset(self):
        review = self._get_review()
        return ReviewReply.objects.filter(
            review=review, is_deleted=False
        ).select_related("author")

    def perform_create(self, serializer):
        review = self._get_review()
        reply = serializer.save(author=self.request.user, review=review)
        # Tell the review author someone answered them — but not when they
        # reply under their own review.
        if review.author_id != self.request.user.id:
            notify(
                review.author,
                "review_reply",
                review_id=review.id,
                place_id=review.place_id,
                place_name=review.place.name,
                reply_author=self.request.user.username or "",
                text_preview=reply.text[:120],
            )


@extend_schema(tags=["reviews"], summary="Delete own reply (author or admin)")
class ReviewReplyDeleteView(views.APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk: int):
        reply = get_object_or_404(ReviewReply, pk=pk, is_deleted=False)
        if reply.author_id != request.user.id and not request.user.is_staff:
            return Response(
                {"detail": "You can only delete your own replies."},
                status=status.HTTP_403_FORBIDDEN,
            )
        reply.is_deleted = True
        reply.save(update_fields=["is_deleted"])
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["reviews"], summary="List reviews pending moderation (admin)")
class ReviewModerationListView(ListAPIView):
    """Admin-only list of reviews pending moderation."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Review.objects.filter(
            is_moderated=False, is_deleted=False
        ).select_related("author", "place")


@extend_schema(
    tags=["reviews"],
    summary="Approve or reject a review (admin)",
    request=inline_serializer(
        name="ReviewModerationActionRequest",
        fields={"reason": drf_serializers.CharField(required=False, allow_blank=True)},
    ),
    responses={
        200: ReviewSerializer,
        400: OpenApiResponse(description="Unknown action."),
    },
)
class ReviewModerationActionView(UpdateAPIView):
    """Admin endpoint to approve/reject a review (action_name from URL)."""

    permission_classes = [IsAdminUser]
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    http_method_names = ["patch", "post"]

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        action_name = self.kwargs.get("action_name")
        reason = request.data.get("reason", "") if hasattr(request, "data") else ""
        if action_name == "approve":
            review.is_moderated = True
            review.is_deleted = False
            review.save(update_fields=["is_moderated", "is_deleted"])
            if review.place_id:
                review.place.recalculate_rating_from_reviews()
        elif action_name == "reject":
            review.is_moderated = False
            review.is_deleted = True
            review.save(update_fields=["is_moderated", "is_deleted"])
            if review.place_id:
                review.place.recalculate_rating_from_reviews()
        else:
            return Response(
                {"detail": "Unknown moderation action."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ModerationLog.objects.create(
            actor=request.user,
            target_type=ModerationLog.TARGET_REVIEW,
            target_id=review.id,
            action=action_name,
            reason=reason or "",
        )
        notify(
            review.author,
            "review_approved" if action_name == "approve" else "review_rejected",
            review_id=review.id,
            place_id=review.place_id,
            place_name=review.place.name if review.place_id else "",
            reason=reason or "",
        )
        logger.info("Review %s %sd by %s", review.id, action_name, request.user)
        return Response(self.get_serializer(review).data)


# Kept for backward compatibility — a thin POST endpoint used by an older URL.
class ReviewCreateView(PlaceReviewsListCreateView):
    """Create a new review for a place via /reviews/create/<place_id>/."""

    http_method_names = ["post"]

    def get_queryset(self):
        return Review.objects.none()
