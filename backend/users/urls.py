from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .jwt_views import EmailTokenObtainPairView
from .views import (
    ChangePasswordView,
    LogoutView,
    MeView,
    RegisterView,
    UserBanView,
    UserViewSet,
)

urlpatterns = [
    # Auth
    path("register/", RegisterView.as_view(), name="user-register"),
    path("login/", EmailTokenObtainPairView.as_view(), name="user-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="user-token-refresh"),
    path("logout/", LogoutView.as_view(), name="user-logout"),
    # Self
    path("me/", MeView.as_view(), name="user-me"),
    path(
        "me/change-password/",
        ChangePasswordView.as_view(),
        name="user-change-password",
    ),
    # Admin
    path("list/", UserViewSet.as_view({"get": "list"}), name="user-list"),
    path(
        "<int:pk>/ban/",
        UserBanView.as_view(),
        {"action": "ban"},
        name="user-ban",
    ),
    path(
        "<int:pk>/unban/",
        UserBanView.as_view(),
        {"action": "unban"},
        name="user-unban",
    ),
    path(
        "<int:pk>/",
        UserViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="user-detail",
    ),
    # Backwards compatibility
    path("create/", RegisterView.as_view(), name="user-create"),
]
