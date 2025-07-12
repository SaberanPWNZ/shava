from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlaceViewSet, PlaceRatingViewSet

router = DefaultRouter()
router.register(r"places", PlaceViewSet)
router.register(r"ratings", PlaceRatingViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
