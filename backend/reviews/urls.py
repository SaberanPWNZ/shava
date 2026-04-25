from django.urls import path, include, re_path
from rest_framework.routers import SimpleRouter

from .views import (
    PlaceReviewsListCreateView,
    ReviewCreateView,
    ReviewModerationActionView,
    ReviewModerationListView,
    ReviewViewSet,
)

router = SimpleRouter()
router.register(r"my-reviews", ReviewViewSet, basename="my-reviews")

urlpatterns = [
    path("", include(router.urls)),
    # Admin moderation
    path(
        "moderation/",
        ReviewModerationListView.as_view(),
        name="reviews-moderation",
    ),
    re_path(
        r"^(?P<pk>\d+)/(?P<action_name>approve|reject)/$",
        ReviewModerationActionView.as_view(),
        name="review-moderation-action",
    ),
    # Public list of approved reviews for a place
    path(
        "reviews/<int:place_pk>/",
        PlaceReviewsListCreateView.as_view(),
        name="place-reviews",
    ),
    path("reviews/create/<int:place_pk>/", ReviewCreateView.as_view(), name="create-review"),
    # Back-compat URL kept from previous version
    path("reviews/create/", ReviewCreateView.as_view(), name="create-review-legacy"),
]
