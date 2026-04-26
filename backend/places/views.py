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
from rest_framework import permissions, serializers as drf_serializers, status, viewsets
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

from places.models import ModerationLog, Place, PlaceRating
from places.permissions import IsAuthorOrAdminOrReadOnly
from places.serializers import (
    ModerationLogSerializer,
    PlaceCreateSerializer,
    PlaceDetailSerializer,
    PlaceRatingSerializer,
    PlaceSerializer,
    PlaceUpdateSerializer,
)

logger = logging.getLogger("places")


PUBLIC_VISIBLE_STATUSES = ("Active", "Approved")


def _apply_place_filters(queryset, params):
    """Apply user-supplied query-param filters to a Place queryset."""
    city = params.get("city")
    if city:
        # Accept either a numeric City PK, a slug, or a free-text name and
        # match against both the FK and the legacy CharField for back-compat.
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
            # Stars are stored at half-scale; multiply by 2 to compare to rating field.
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
        # Staff can request any status via ?status=
        status_filter = params.get("status")
        if status_filter and user.is_authenticated and user.is_staff:
            qs = Place.objects.filter(status=status_filter)
        else:
            qs = Place.objects.filter(status__in=PUBLIC_VISIBLE_STATUSES)
        # ``?author=me`` (or ?author=<id>) — used by the profile "my places"
        # tab. ``me`` is resolved to the authenticated user's PK; when used
        # by an authenticated owner we widen the queryset back to *all*
        # statuses so pending submissions are visible too.
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
        # Annotate aggregate columns the serializer would otherwise compute
        # one-place-at-a-time. Keeps the list endpoint at constant query
        # count regardless of page size.
        qs = qs.with_list_annotations().select_related("city_ref", "author")
        return _apply_place_filters(qs, params)


@extend_schema(tags=["places"], summary="Submit a new place (goes to moderation)")
class PlaceCreateView(CreateAPIView):
    """Authenticated users submit a new place; always created on moderation."""

    serializer_class = PlaceCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        try:
            instance = serializer.save(author=self.request.user)
            # Force moderation regardless of payload.
            if instance.status not in ("On_moderation",):
                instance.status = "On_moderation"
                instance.save(update_fields=["status"])
            logger.info("Place submitted: %s by %s", instance.name, self.request.user)
            return instance
        except ValidationError as e:
            logger.error("Validation error creating place: %s", e)
            # Surface only the user-facing messages produced by model validators
            # (a list of plain strings). Avoid `str(e)`, which leaks the
            # internal repr of the exception (CodeQL py/stack-trace-exposure).
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
        if obj.status not in PUBLIC_VISIBLE_STATUSES:
            user = self.request.user
            # Authenticated users can view any place (e.g. their own pending
            # submissions); anonymous users only see public statuses.
            if not user.is_authenticated:
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
        return Place.objects.all()


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
        stored = stars * 2  # 1-5 stars -> 2-10 internal scale
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
