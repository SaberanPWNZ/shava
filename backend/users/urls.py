from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserCreateViewSet

router = DefaultRouter()
router.register("", UserViewSet)

urlpatterns = [
    path("create/", UserCreateViewSet.as_view(), name="user-create"),
]
