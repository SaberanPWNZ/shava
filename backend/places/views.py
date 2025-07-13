import logging
from rest_framework import viewsets, permissions
from places.models import Place
from places.serializers import PlaceSerializer

logger = logging.getLogger("places")


class PlaceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Place instances with full CRUD operations.
    
    Provides:
    - list: GET /api/places/ - Get all places
    - create: POST /api/places/ - Create a new place
    - retrieve: GET /api/places/{id}/ - Get a specific place
    - update: PUT /api/places/{id}/ - Update a place (full update)
    - partial_update: PATCH /api/places/{id}/ - Update a place (partial update)
    - destroy: DELETE /api/places/{id}/ - Delete a place
    """
    
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Allow read access to everyone, but require authentication for modifications
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Log place creation"""
        logger.info("User %s creating new place", self.request.user)
        place = serializer.save()
        logger.info("Place created successfully with ID: %s", place.id)

    def perform_update(self, serializer):
        """Log place update"""
        logger.info("User %s updating place with ID: %s", self.request.user, serializer.instance.id)
        place = serializer.save()
        logger.info("Place with ID %s updated successfully", place.id)

    def perform_destroy(self, instance):
        """Log place deletion"""
        logger.info("User %s deleting place with ID: %s", self.request.user, instance.id)
        place_name = instance.name
        instance.delete()
        logger.info("Place '%s' with ID %s deleted successfully", place_name, instance.id)
