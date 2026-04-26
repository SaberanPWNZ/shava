from django.urls import path

from .views import (
    BadgeCatalogueView,
    LeaderboardView,
    MeGamificationView,
    MyPointsTransactionsView,
    PublicUserGamificationView,
)

urlpatterns = [
    path("me/", MeGamificationView.as_view(), name="gamification-me"),
    path(
        "me/transactions/",
        MyPointsTransactionsView.as_view(),
        name="gamification-me-transactions",
    ),
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
