from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.permissions import AllowAny

from places.models import Place
from places_menu.models import Menu
from places_menu.serializers import MenuItemSerializer


class IsPlaceAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """Read for everyone; write only for the place author or staff."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not (request.user and request.user.is_authenticated):
            return False
        place = view.get_place()
        return request.user.is_staff or place.author_id == request.user.id


class PlaceMenuViewSet(viewsets.ModelViewSet):
    """Menu items for a specific place. URL kwarg: place_pk."""

    serializer_class = MenuItemSerializer
    permission_classes = [IsPlaceAuthorOrAdminOrReadOnly]

    def get_permissions(self):
        # Public reads — overrides REST_FRAMEWORK default IsAuthenticated.
        if self.request.method in permissions.SAFE_METHODS:
            return [AllowAny()]
        return super().get_permissions()

    def get_place(self):
        if not hasattr(self, "_place"):
            self._place = get_object_or_404(Place, pk=self.kwargs.get("place_pk"))
        return self._place

    def get_queryset(self):
        return Menu.objects.filter(place_id=self.kwargs.get("place_pk"))

    def perform_create(self, serializer):
        place = self.get_place()
        serializer.save(place=place)

    def perform_update(self, serializer):
        place = self.get_place()
        serializer.save(place=place)
