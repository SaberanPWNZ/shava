"""URL patterns mounted under /api/places/<place_pk>/reviews/."""

from django.urls import path

from reviews.views import (
    PlaceReviewsListCreateView,
)

urlpatterns = [
    path("", PlaceReviewsListCreateView.as_view(), name="place-reviews"),
]
