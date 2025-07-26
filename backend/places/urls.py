from django.urls import path
from .views import (
    PlaceCreateView,
    PlaceDetailView,
    PlaceUpdateView,
    PlaceListView,
)

urlpatterns = [
    path("places/", PlaceListView.as_view(), name="places-list"),
    path("places/<int:pk>/", PlaceDetailView.as_view(), name="place-detail"),
    path("submit-place/", PlaceCreateView.as_view(), name="submit-place"),
    path("places/<int:pk>/update/", PlaceUpdateView.as_view(), name="update-place"),
]
