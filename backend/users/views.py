"""Views for the users app.

JWT-only authentication on every endpoint. Privileged actions are gated by
custom permissions in :mod:`users.permissions`. Business logic lives in
:mod:`users.services` (SRP) and token operations go through the
``TokenIssuer`` abstraction in :mod:`users.token_issuer` (DIP).
"""
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.models import User
from users.permissions import IsAdmin, IsSelfOrAdmin
from users.serializers import (
    ChangePasswordSerializer,
    MeUpdateSerializer,
    RegisterSerializer,
    UserAdminSerializer,
    UserPublicSerializer,
)
from users.services import UserRegistrationService
from users.token_issuer import SimpleJWTTokenIssuer, TokenError


class RegisterView(generics.CreateAPIView):
    """Public user registration.

    Accepts only the whitelisted fields from :class:`RegisterSerializer`,
    so privilege-escalation via extra payload fields is impossible.
    """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes: list = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["registration_service"] = UserRegistrationService()
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserPublicSerializer(user).data, status=status.HTTP_201_CREATED
        )


class MeView(APIView):
    """``/me/`` — get or partially update the current user's profile."""

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        return Response(UserPublicSerializer(request.user).data)

    def patch(self, request):
        serializer = MeUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserPublicSerializer(request.user).data)


class ChangePasswordView(APIView):
    """Change the password of the authenticated user."""

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class LogoutView(APIView):
    """Blacklist the supplied refresh token to log the user out."""

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    token_issuer = SimpleJWTTokenIssuer()

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"refresh": "This field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            self.token_issuer.revoke_refresh_token(refresh)
        except TokenError:
            return Response(
                {"refresh": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_205_RESET_CONTENT)


class UserViewSet(viewsets.ModelViewSet):
    """Admin-only CRUD for users.

    Permissions are returned as fresh instances per request — never mutated
    on the class — to avoid leaking permissions between requests.
    """

    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated(), IsSelfOrAdmin()]
        return [IsAuthenticated(), IsAdmin()]

    def get_serializer_class(self):
        # Non-admins listing/retrieving see only the safe representation.
        if self.action in ("list", "retrieve"):
            user = self.request.user
            is_admin = bool(
                user.is_authenticated
                and (
                    user.is_staff
                    or user.is_superuser
                    or getattr(user, "is_admin", False)
                )
            )
            if not is_admin:
                return UserPublicSerializer
        return UserAdminSerializer
