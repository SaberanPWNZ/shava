from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AchievementViewSet, UserAchievementViewSet, UserRatingViewSet

router = DefaultRouter()
router.register(r"achievements", AchievementViewSet)
router.register(r"user-ratings", UserRatingViewSet)
router.register(r"user-achievements", UserAchievementViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
