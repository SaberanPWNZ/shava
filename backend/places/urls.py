from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PlaceCreateView,
    PlaceRatingViewSet,
    PlaceDetailView,
    PlaceUpdateView,
    PlaceModerationViewSet,
    PlaceListView,
)

router = DefaultRouter()
router.register(r"ratings", PlaceRatingViewSet, basename="place-rating")
router.register(
    r"admin/moderation", PlaceModerationViewSet, basename="place-moderation"
)

urlpatterns = [
    path("", include(router.urls)),
    path("places/", PlaceListView.as_view(), name="places-list"),
    path("places/<int:pk>/", PlaceDetailView.as_view(), name="place-detail"),
    path("submit-place/", PlaceCreateView.as_view(), name="submit-place"),
    path("places/<int:pk>/update/", PlaceUpdateView.as_view(), name="update-place"),
]
