from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView  # type: ignore
from rest_framework.permissions import IsAuthenticated  # type: ignore
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError
import logging

from places.models import Place, PlaceRating
from places.serializers import (
    PlaceCreateSerializer,
    PlaceRatingSerializer,
    PlaceUpdateSerializer,
)

logger = logging.getLogger("places")


class PlaceCreateView(CreateAPIView):
    """
    API endpoint that allows places to be created.
    """

    queryset = Place.objects.all()
    serializer_class = PlaceCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        """Override to add custom creation logic"""
        try:
            instance = serializer.save()
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
    queryset = Place.objects.all()
    serializer_class = PlaceUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # додати JSONParser

    def perform_update(self, serializer):
        """Override to add custom update logic"""
        try:
            instance = serializer.save()
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
    queryset = PlaceRating.objects.all()
    serializer_class = PlaceRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PlaceRating.objects.filter(user=self.request.user)

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
        return instance
        return instance
