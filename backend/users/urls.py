from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserDetailView, UserViewSet, UserCreateViewSet

router = DefaultRouter()
router.register("", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("create/", UserCreateViewSet.as_view(), name="user-create"),
    path("me/", UserDetailView.as_view(), name="user-detail"),
]
