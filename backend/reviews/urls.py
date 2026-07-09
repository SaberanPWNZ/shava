from django.urls import include, path, re_path
from rest_framework.routers import SimpleRouter

from gamification.views import ReviewHelpfulView

from .views import (
    PlaceReviewsListCreateView,
    ReviewCreateView,
    ReviewFeedView,
    ReviewModerationActionView,
    ReviewModerationListView,
    ReviewRepliesListCreateView,
    ReviewReplyDeleteView,
    ReviewViewSet,
    UserReviewsListView,
)

router = SimpleRouter()
router.register(r"my-reviews", ReviewViewSet, basename="my-reviews")

urlpatterns = [
    path("", include(router.urls)),
    # Public site-wide feed of latest approved reviews
    path("feed/", ReviewFeedView.as_view(), name="reviews-feed"),
    # Public list of one user's approved reviews (profile pages)
    path(
        "by-user/<int:user_pk>/",
        UserReviewsListView.as_view(),
        name="reviews-by-user",
    ),
    # Replies (threaded discussion under a review)
    path(
        "<int:pk>/replies/",
        ReviewRepliesListCreateView.as_view(),
        name="review-replies",
    ),
    path(
        "replies/<int:pk>/",
        ReviewReplyDeleteView.as_view(),
        name="review-reply-delete",
    ),
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
    # Helpful votes (gamification integration)
    path(
        "<int:pk>/helpful/",
        ReviewHelpfulView.as_view(),
        name="review-helpful",
    ),
    # Public list of approved reviews for a place
    path(
        "reviews/<int:place_pk>/",
        PlaceReviewsListCreateView.as_view(),
        name="place-reviews",
    ),
    path(
        "reviews/create/<int:place_pk>/",
        ReviewCreateView.as_view(),
        name="create-review",
    ),
    # Back-compat URL kept from previous version
    path("reviews/create/", ReviewCreateView.as_view(), name="create-review-legacy"),
]
