from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    ListAPIView,
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError
import logging

from places.models import Place, PlaceRating
from places.serializers import (
    PlaceCreateSerializer,
    PlaceRatingSerializer,
    PlaceUpdateSerializer,
    PlaceSerializer,  # Remove PlaceModerationSerializer
)

logger = logging.getLogger("places")


class PlaceCreateView(CreateAPIView):
    """
    API endpoint that allows places to be created.
    """

    serializer_class = PlaceCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Place.objects.all()

    def perform_create(self, serializer):
        """Override to add custom creation logic and moderation"""
        try:
            instance = serializer.save(author=self.request.user)

            logger.info(
                f"Place created successfully: {instance.name} by user {self.request.user}"
            )
            return instance
        except ValidationError as e:
            logger.error(f"Validation error creating place: {e}")
            raise DRFValidationError({"detail": str(e)})
        except Exception as e:
            logger.error(f"Unexpected error creating place: {e}", exc_info=True)
            raise DRFValidationError({"detail": "Failed to create place"})


class PlaceUpdateView(UpdateAPIView, RetrieveAPIView):
    serializer_class = PlaceUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return Place.objects.all()

    def perform_update(self, serializer):
        """Override to add custom update logic and moderation"""
        try:
            instance = serializer.save()
            if not (self.request.user.is_staff or self.request.user.is_superuser):
                # automoderate(instance, self.request.user)  # Removed temporary moderation
                pass

            logger.info(
                f"Place updated successfully: {instance.name} by user {self.request.user}"
            )
            return instance
        except ValidationError as e:
            logger.error(f"Validation error updating place: {e}")
            raise DRFValidationError({"detail": str(e)})


class PlaceDetailView(RetrieveAPIView):
    """
    API endpoint that allows a place to be viewed by id.
    """

    serializer_class = PlaceCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = "pk"

    def get_queryset(self):
        """Optimize queryset with select_related/prefetch_related"""
        return Place.objects.select_related().prefetch_related("ratings", "review_set")

    def get(self, request, *args, **kwargs):
        try:
            place = self.get_object()
            serializer = self.get_serializer(place)
            logger.info(f"Place detail viewed: {place.name} by user {request.user}")
            return Response(serializer.data)
        except (Place.DoesNotExist, Exception) as e:
            if "No Place matches the given query" in str(e) or "does not exist" in str(
                e
            ):
                logger.warning(f"Place with pk={kwargs.get('pk')} not found")
                return Response(
                    {"detail": "Place not found."}, status=status.HTTP_404_NOT_FOUND
                )
            else:
                logger.error(
                    f"Unexpected error in PlaceDetailView.get: {e}", exc_info=True
                )
                return Response(
                    {"detail": "Internal server error"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )


class PlaceRatingViewSet(viewsets.ModelViewSet):
    serializer_class = PlaceRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request, "user"):
            return PlaceRating.objects.filter(user=self.request.user)
        return PlaceRating.objects.none()

    @action(detail=False, methods=["post"], url_path="rate-place")
    def rate_place(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        """Override to add logging"""
        instance = serializer.save()
        logger.info(
            f"Rating created: {instance.rating} for place {instance.place.name} by {self.request.user}"
        )
        return instance

    def perform_update(self, serializer):
        """Override to add logging"""
        instance = serializer.save()
        logger.info(
            f"Rating updated: {instance.rating} for place {instance.place.name} by {self.request.user}"
        )
        return instance


class PlaceModerationViewSet(viewsets.ViewSet):
    """
    ViewSet for handling place moderation actions with custom moderation
    """

    permission_classes = [IsAdminUser]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a place"""
        try:
            place = Place.objects.get(pk=pk, status="On_moderation")
            reason = request.data.get("reason", "Approved by moderator")
            place.approve(request.user, reason)

            logger.info(f"Place {pk} approved by {request.user}")
            return Response({"status": "approved"}, status=status.HTTP_200_OK)
        except Place.DoesNotExist:
            return Response(
                {"error": "Place not found or not pending moderation"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error approving place: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Reject a place"""
        try:
            place = Place.objects.get(pk=pk, status="On_moderation")
            reason = request.data.get("reason", "Rejected by moderator")
            place.reject(request.user, reason)

            logger.info(f"Place {pk} rejected by {request.user}")
            return Response({"status": "rejected"}, status=status.HTTP_200_OK)
        except Place.DoesNotExist:
            return Response(
                {"error": "Place not found or not pending moderation"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error rejecting place: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def pending(self, request):
        """Get list of places pending moderation"""
        try:
            pending_places = Place.objects.filter(status="On_moderation")
            serializer = PlaceSerializer(pending_places, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching pending places: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PlaceListView(ListAPIView):
    """List view for approved places only (public access)."""

    serializer_class = PlaceSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Return only active/approved places."""
        return Place.objects.filter(status__in=["Active", "Approved"])
        return Place.objects.filter(status__in=["Active", "Approved"])


class PlaceListView(ListAPIView):
    """List view for approved places only (public access)."""

    serializer_class = PlaceSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Return only approved places."""
        return Place.objects.filter(status="Approved")
