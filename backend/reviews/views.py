from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ValidationError
import logging

from reviews.models import Review
from reviews.serializers import ReviewSerializer, ReviewCreateSerializer
from places.models import Place

logger = logging.getLogger("reviews")


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reviews
    """

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return reviews for the authenticated user"""
        return Review.objects.filter(author=self.request.user, is_deleted=False)

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == "create":
            return ReviewCreateSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        """Override to set the author and add logging"""
        try:
            instance = serializer.save(author=self.request.user)
            logger.info(
                f"Review created: {instance.score} for place {instance.place.name} by {self.request.user}"
            )
            return instance
        except Exception as e:
            logger.error(f"Error creating review: {e}")
            raise

    def perform_destroy(self, instance):
        """Soft delete instead of hard delete"""
        instance.is_deleted = True
        instance.save()
        logger.info(f"Review soft deleted: {instance.id} by {self.request.user}")


class PlaceReviewsListView(ListAPIView):
    """
    List all reviews for a specific place (public access)
    """

    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        place_id = self.kwargs.get("place_id")
        return Review.objects.filter(
            place_id=place_id, is_deleted=False, is_moderated=True
        ).select_related("author", "place")


class ReviewCreateView(CreateAPIView):
    """
    Create a new review for a place
    """

    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Override to set the author"""
        place_id = self.kwargs.get("place_id")
        place = get_object_or_404(Place, id=place_id)

        if Review.objects.filter(
            author=self.request.user, place=place, is_deleted=False
        ).exists():
            raise ValidationError("You have already reviewed this place.")

        serializer.save(author=self.request.user, place=place)
        logger.info(f"Review created for place {place.name} by {self.request.user}")
