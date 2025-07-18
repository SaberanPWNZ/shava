from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PlaceCreateView,
    PlaceRatingViewSet,
    PlaceDetailView,
    PlaceUpdateView,
    PlaceModerationViewSet,
)

router = DefaultRouter()
router.register(r"ratings", PlaceRatingViewSet, basename="place-rating")
router.register(r"moderation", PlaceModerationViewSet, basename="place-moderation")

urlpatterns = [
    path("", include(router.urls)),
    path("create-place/", PlaceCreateView.as_view(), name="create-place"),
    path("place/<int:pk>/", PlaceDetailView.as_view(), name="place-detail"),
    path("<int:pk>/", PlaceUpdateView.as_view(), name="update-place"),
]
