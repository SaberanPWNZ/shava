from django.urls import path, include
from rest_framework.routers import DefaultRouter
from places.views import PlaceViewSet

router = DefaultRouter()
router.register('', PlaceViewSet, basename='place')

urlpatterns = [
    path('', include(router.urls)),
]