from django.urls import path
from .views import UserDetailView, UserViewSet, UserCreateViewSet

urlpatterns = [
    path("list/", UserViewSet.as_view({"get": "list"}), name="user-list"),
    path("<int:pk>/", UserViewSet.as_view({"get": "retrieve"}), name="user-detail"),
    path("create/", UserCreateViewSet.as_view(), name="user-create"),
    path("me/", UserDetailView.as_view(), name="user-profile"),
]
