from django.urls import path

from .views import (
    BadgeCatalogueView,
    LeaderboardView,
    MeGamificationView,
    PublicUserGamificationView,
)

urlpatterns = [
    path("me/", MeGamificationView.as_view(), name="gamification-me"),
    path(
        "users/<int:pk>/public/",
        PublicUserGamificationView.as_view(),
        name="gamification-public",
    ),
    path("badges/", BadgeCatalogueView.as_view(), name="gamification-badges"),
    path(
        "leaderboard/",
        LeaderboardView.as_view(),
        name="gamification-leaderboard",
    ),
]
