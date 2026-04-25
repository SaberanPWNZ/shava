from django.urls import path, include, re_path
from rest_framework.routers import SimpleRouter

from .views import (
    PlaceCreateView,
    PlaceDetailView,
    PlaceListView,
    PlaceModerationActionView,
    PlaceModerationListView,
    PlaceRateView,
    PlaceRatingViewSet,
    PlaceUpdateView,
)

router = SimpleRouter()
router.register(r"ratings", PlaceRatingViewSet, basename="place-ratings")

urlpatterns = [
    # User ratings management
    path("", include(router.urls)),
    # Public list and submission
    path("", PlaceListView.as_view(), name="places-list"),
    path("create-place/", PlaceCreateView.as_view(), name="create-place"),
    path("submit-place/", PlaceCreateView.as_view(), name="submit-place"),
    path("moderation/", PlaceModerationListView.as_view(), name="places-moderation"),
    # Public detail (kept under /place/<pk>/ for back-compat with existing tests)
    path("place/<int:pk>/", PlaceDetailView.as_view(), name="place-detail"),
    # Per-place menu / reviews / moderation actions / rate
    path("<int:place_pk>/menu/", include("places_menu.urls")),
    path("<int:place_pk>/reviews/", include("reviews.place_urls")),
    path("<int:pk>/rate/", PlaceRateView.as_view(), name="place-rate"),
    re_path(
        r"^(?P<pk>\d+)/(?P<action_name>approve|reject)/$",
        PlaceModerationActionView.as_view(),
        name="place-moderation-action",
    ),
    # Update (author/admin) — must be last because <int:pk>/ matches everything
    path("<int:pk>/", PlaceUpdateView.as_view(), name="update-place"),
]
