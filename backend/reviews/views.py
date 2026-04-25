import logging

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.generics import ListAPIView, ListCreateAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from places.models import Place
from reviews.models import Review
from reviews.serializers import ReviewCreateSerializer, ReviewSerializer

logger = logging.getLogger("reviews")


class ReviewViewSet(viewsets.ModelViewSet):
    """A user's own reviews."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(
            author=self.request.user, is_deleted=False
        ).select_related("place")

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

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save(update_fields=["is_deleted"])
        # Recompute the place rating in case the deleted review was approved.
        if instance.place_id:
            instance.place.recalculate_rating_from_reviews()


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
        qs = Review.objects.filter(place_id=place_id, is_deleted=False)
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return qs
        # Authors see their own pending reviews + everyone's approved reviews.
        if user.is_authenticated:
            from django.db.models import Q

            return qs.filter(Q(is_moderated=True) | Q(author=user))
        return qs.filter(is_moderated=True)

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


class ReviewModerationListView(ListAPIView):
    """Admin-only list of reviews pending moderation."""

    serializer_class = ReviewSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Review.objects.filter(
            is_moderated=False, is_deleted=False
        ).select_related("author", "place")


class ReviewModerationActionView(UpdateAPIView):
    """Admin endpoint to approve/reject a review (action_name from URL)."""

    permission_classes = [IsAdminUser]
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    http_method_names = ["patch", "post"]

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        action_name = self.kwargs.get("action_name")
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
        logger.info(
            "Review %s %sd by %s", review.id, action_name, request.user
        )
        return Response(self.get_serializer(review).data)


# Kept for backward compatibility — a thin POST endpoint used by an older URL.
class ReviewCreateView(PlaceReviewsListCreateView):
    """Create a new review for a place via /reviews/create/<place_id>/."""

    http_method_names = ["post"]

    def get_queryset(self):
        return Review.objects.none()
