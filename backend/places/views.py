import logging
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import permissions, status, views, viewsets
from rest_framework import serializers as drf_serializers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from notifications.services import notify
from places.models import City, ModerationLog, Place, PlaceFavorite, PlaceRating
from places.permissions import IsAuthorOrAdminOrReadOnly
from places.serializers import (
    CityMinimalSerializer,
    ModerationLogSerializer,
    PlaceCreateSerializer,
    PlaceDetailSerializer,
    PlaceRatingSerializer,
    PlaceSerializer,
    PlaceUpdateSerializer,
)

logger = logging.getLogger("places")


PUBLIC_VISIBLE_STATUSES = ("Active", "Approved")


def _can_view_nonpublic_place(user, place) -> bool:
    """Whether ``user`` may view ``place`` while it is not publicly visible.

    Only the place's own author or staff may see non-public statuses
    (pending moderation, rejected, ...). Everyone else — including other
    authenticated users and anonymous visitors — must be treated as if the
    place does not exist.
    """
    if not (user and user.is_authenticated):
        return False
    if user.is_staff:
        return True
    author = getattr(place, "author", None)
    return author is not None and author == user


@extend_schema(tags=["places"], summary="List active cities (for filters/registration)")
class CityListView(ListAPIView):
    """Public, unpaginated list of active cities.

    Small reference table (~20 rows) — the frontend uses this to populate
    the city dropdown on the places filter bar and the registration form,
    so pagination would just add friction for no benefit.
    """

    serializer_class = CityMinimalSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    queryset = City.objects.filter(is_active=True).order_by("name")


def _apply_place_filters(queryset, params):
    """Apply user-supplied query-param filters to a Place queryset."""
    city = params.get("city")
    if city:
        cond = (
            Q(city__iexact=city)
            | Q(city_ref__slug__iexact=city)
            | Q(city_ref__name__iexact=city)
        )
        if str(city).isdigit():
            cond |= Q(city_ref_id=int(city))
        queryset = queryset.filter(cond)

    district = params.get("district")
    if district:
        queryset = queryset.filter(district=district)

    delivery = params.get("delivery")
    if delivery is not None and delivery != "":
        queryset = queryset.filter(
            delivery=str(delivery).lower() in ("1", "true", "yes")
        )

    is_featured = params.get("is_featured")
    if is_featured is not None and is_featured != "":
        queryset = queryset.filter(
            is_featured=str(is_featured).lower() in ("1", "true", "yes")
        )

    min_rating = params.get("min_rating")
    if min_rating not in (None, ""):
        try:
            queryset = queryset.filter(rating__gte=Decimal(str(min_rating)))
        except (InvalidOperation, ValueError):
            pass

    min_stars = params.get("min_stars")
    if min_stars not in (None, ""):
        try:
            queryset = queryset.filter(rating__gte=Decimal(str(min_stars)) * 2)
        except (InvalidOperation, ValueError):
            pass

    has_menu = params.get("has_menu")
    if has_menu is not None and has_menu != "":
        if str(has_menu).lower() in ("1", "true", "yes"):
            queryset = queryset.filter(menus__isnull=False).distinct()

    search = params.get("search")
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    ordering = params.get("ordering")
    allowed_ordering = {
        "rating",
        "-rating",
        "created_at",
        "-created_at",
        "name",
        "-name",
    }
    if ordering in allowed_ordering:
        queryset = queryset.order_by(ordering)
    return queryset


@extend_schema(
    tags=["places"],
    parameters=[
        OpenApiParameter("search", str, OpenApiParameter.QUERY, required=False),
        OpenApiParameter("city", str, OpenApiParameter.QUERY, required=False),
        OpenApiParameter("district", str, OpenApiParameter.QUERY, required=False),
        OpenApiParameter("delivery", bool, OpenApiParameter.QUERY, required=False),
        OpenApiParameter("is_featured", bool, OpenApiParameter.QUERY, required=False),
        OpenApiParameter("min_stars", float, OpenApiParameter.QUERY, required=False),
        OpenApiParameter("min_rating", float, OpenApiParameter.QUERY, required=False),
        OpenApiParameter("has_menu", bool, OpenApiParameter.QUERY, required=False),
        OpenApiParameter(
            "ordering",
            str,
            OpenApiParameter.QUERY,
            required=False,
            enum=[
                "rating",
                "-rating",
                "created_at",
                "-created_at",
                "name",
                "-name",
            ],
        ),
        OpenApiParameter(
            "author",
            str,
            OpenApiParameter.QUERY,
            required=False,
            description="Filter to a specific author user id, or 'me' for the current user.",
        ),
    ],
)
class PlaceListView(ListAPIView):
    """Public list of approved/active places, with filters."""

    serializer_class = PlaceSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        params = self.request.query_params
        user = self.request.user
        status_filter = params.get("status")
        if status_filter and user.is_authenticated and user.is_staff:
            qs = Place.objects.filter(status=status_filter)
        else:
            qs = Place.objects.filter(status__in=PUBLIC_VISIBLE_STATUSES)
        author = params.get("author")
        if author:
            if author == "me":
                if user.is_authenticated:
                    qs = Place.objects.filter(author=user)
                else:
                    qs = Place.objects.none()
            else:
                try:
                    qs = qs.filter(author_id=int(author))
                except (TypeError, ValueError):
                    qs = qs.none()
        qs = (
            qs.with_list_annotations()
            .with_viewer_favorites(user)
            .select_related("city_ref", "author")
        )
        return _apply_place_filters(qs, params)


class PlaceFavoriteView(views.APIView):
    """POST/DELETE ``/places/<pk>/favorite/`` — toggle a bookmark.

    Idempotent in both directions so double-clicks and retried requests
    never error; the response always carries the fresh aggregate count
    plus the viewer's resulting state.
    """

    permission_classes = [IsAuthenticated]

    _RESPONSE_SERIALIZER = inline_serializer(
        name="PlaceFavoriteResponse",
        fields={
            "favorites_count": drf_serializers.IntegerField(),
            "favorited": drf_serializers.BooleanField(),
        },
    )

    def _get_place(self, pk):
        return get_object_or_404(Place, pk=pk, status__in=PUBLIC_VISIBLE_STATUSES)

    @extend_schema(
        tags=["places"],
        summary="Save a place to the viewer's favorites",
        request=None,
        responses={200: _RESPONSE_SERIALIZER, 201: _RESPONSE_SERIALIZER},
    )
    def post(self, request, pk: int):
        place = self._get_place(pk)
        _, created = PlaceFavorite.objects.get_or_create(user=request.user, place=place)
        return Response(
            {"favorites_count": place.favorites.count(), "favorited": True},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["places"],
        summary="Remove a place from the viewer's favorites",
        request=None,
        responses={200: _RESPONSE_SERIALIZER},
    )
    def delete(self, request, pk: int):
        place = self._get_place(pk)
        PlaceFavorite.objects.filter(user=request.user, place=place).delete()
        return Response(
            {"favorites_count": place.favorites.count(), "favorited": False}
        )


@extend_schema(tags=["places"], summary="List the viewer's favorite places")
class FavoritePlacesListView(ListAPIView):
    """Paginated list of places the current user has bookmarked,
    most recently saved first."""

    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from django.db.models import OuterRef, Subquery

        my_favorites = PlaceFavorite.objects.filter(user=self.request.user)
        # Ordering via a subquery (not a JOIN on `favorites`) so the
        # `_favorites_count` annotation keeps counting *all* users' rows.
        saved_at = my_favorites.filter(place=OuterRef("pk")).values("created_at")[:1]
        return (
            Place.objects.filter(
                id__in=my_favorites.values_list("place_id", flat=True),
                status__in=PUBLIC_VISIBLE_STATUSES,
            )
            .with_list_annotations()
            .with_viewer_favorites(self.request.user)
            .select_related("city_ref", "author")
            .annotate(_saved_at=Subquery(saved_at))
            .order_by("-_saved_at")
        )


@extend_schema(tags=["places"], summary="Submit a new place (goes to moderation)")
class PlaceCreateView(CreateAPIView):
    """Authenticated users submit a new place; always created on moderation."""

    serializer_class = PlaceCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        try:
            instance = serializer.save(author=self.request.user)
            if instance.status not in ("On_moderation",):
                instance.status = "On_moderation"
                instance.save(update_fields=["status"])
            logger.info("Place submitted: %s by %s", instance.name, self.request.user)
            return instance
        except ValidationError as e:
            logger.error("Validation error creating place: %s", e)
            raise DRFValidationError({"detail": e.messages}) from e


@extend_schema(tags=["places"])
class PlaceDetailView(RetrieveAPIView):
    """Public detail view; non-public statuses only visible to author or staff."""

    serializer_class = PlaceDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "pk"

    def get_queryset(self):
        return Place.objects.select_related("author").prefetch_related(
            "ratings", "review_set", "menus"
        )

    def get_object(self):
        obj = super().get_object()
        if obj.status not in PUBLIC_VISIBLE_STATUSES and not _can_view_nonpublic_place(
            self.request.user, obj
        ):
            from django.http import Http404

            raise Http404("Place not found.")
        return obj


@extend_schema(tags=["places"])
class PlaceUpdateView(UpdateAPIView, RetrieveAPIView):
    """Author or admin can edit a place."""

    serializer_class = PlaceUpdateSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return Place.objects.select_related("author").all()

    def get_object(self):
        from django.http import Http404
        from rest_framework.generics import get_object_or_404

        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        if obj.status not in PUBLIC_VISIBLE_STATUSES and not _can_view_nonpublic_place(
            self.request.user, obj
        ):
            raise Http404("Place not found.")
        self.check_object_permissions(self.request, obj)
        return obj


@extend_schema(tags=["places"], summary="List places pending moderation (admin)")
class PlaceModerationListView(ListAPIView):
    """Admin-only list of places pending moderation."""

    serializer_class = PlaceSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return (
            Place.objects.filter(status="On_moderation")
            .with_list_annotations()
            .select_related("city_ref", "author")
            .order_by("-created_at")
        )


@extend_schema(
    tags=["places"],
    summary="Approve or reject a place (admin)",
    request=inline_serializer(
        name="PlaceModerationActionRequest",
        fields={"reason": drf_serializers.CharField(required=False, allow_blank=True)},
    ),
    responses={200: PlaceSerializer},
)
class PlaceModerationActionView(UpdateAPIView):
    """Admin endpoint to approve/reject a place. Action is taken from URL kwargs."""

    permission_classes = [IsAdminUser]
    serializer_class = PlaceSerializer
    queryset = Place.objects.all()
    http_method_names = ["patch", "post"]

    def update(self, request, *args, **kwargs):
        place = self.get_object()
        action_name = self.kwargs.get("action_name")
        reason = request.data.get("reason", "") if hasattr(request, "data") else ""
        if action_name == "approve":
            place.approve(request.user, reason=reason)
        elif action_name == "reject":
            place.reject(request.user, reason=reason)
        else:
            return Response(
                {"detail": "Unknown moderation action."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ModerationLog.objects.create(
            actor=request.user,
            target_type=ModerationLog.TARGET_PLACE,
            target_id=place.id,
            action=action_name,
            reason=reason or "",
        )
        notify(
            place.author,
            "place_approved" if action_name == "approve" else "place_rejected",
            place_id=place.id,
            place_name=place.name,
            reason=reason or "",
        )
        logger.info("Place %s %sd by %s", place.id, action_name, request.user)
        return Response(self.get_serializer(place).data)


@extend_schema(
    tags=["places"],
    summary="List recent moderation actions (admin)",
    responses={200: ModerationLogSerializer(many=True)},
)
class ModerationLogListView(ListAPIView):
    """Admin-only paginated list of recent moderation actions."""

    permission_classes = [IsAdminUser]
    serializer_class = ModerationLogSerializer

    def get_queryset(self):
        return ModerationLog.objects.select_related("actor").all()


@extend_schema(
    tags=["places"],
    summary="Submit a 1–5 star rating",
    request=inline_serializer(
        name="PlaceRateRequest",
        fields={"rating": drf_serializers.DecimalField(max_digits=3, decimal_places=1)},
    ),
    responses={
        201: PlaceRatingSerializer,
        400: OpenApiResponse(description="Invalid rating value."),
    },
)
class PlaceRateView(CreateAPIView):
    """Star-rating endpoint: accepts {rating: 1..5}, stored on 0-10 scale."""

    permission_classes = [IsAuthenticated]
    serializer_class = PlaceRatingSerializer

    def create(self, request, *args, **kwargs):
        place = get_object_or_404(Place, pk=self.kwargs.get("pk"))
        raw = request.data.get("rating")
        if raw is None:
            return Response(
                {"rating": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            stars = Decimal(str(raw))
        except (InvalidOperation, ValueError):
            return Response(
                {"rating": ["Must be a number between 1 and 5."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if stars < 1 or stars > 5:
            return Response(
                {"rating": ["Must be between 1 and 5."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        stored = stars * 2
        rating_obj, _ = PlaceRating.objects.update_or_create(
            user=request.user, place=place, defaults={"rating": stored}
        )
        place.update_rating()
        return Response(
            PlaceRatingSerializer(rating_obj).data, status=status.HTTP_201_CREATED
        )


@extend_schema(tags=["places"])
class PlaceRatingViewSet(viewsets.ModelViewSet):
    """A user's own ratings (for management UI)."""

    serializer_class = PlaceRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request, "user") and self.request.user.is_authenticated:
            return PlaceRating.objects.filter(user=self.request.user)
        return PlaceRating.objects.none()

    @action(detail=False, methods=["post"], url_path="rate-place")
    def rate_place(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
