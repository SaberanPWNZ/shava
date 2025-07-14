from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlaceCreateView, PlaceRatingViewSet

router = DefaultRouter()
router.register(r"ratings", PlaceRatingViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("create-place/", PlaceCreateView.as_view(), name="create-place"),
]
