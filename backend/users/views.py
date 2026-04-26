"""Views for the users app.

JWT-only authentication on every endpoint. Privileged actions are gated by
custom permissions in :mod:`users.permissions`. Business logic lives in
:mod:`users.services` (SRP) and token operations go through the
``TokenIssuer`` abstraction in :mod:`users.token_issuer` (DIP).
"""

import logging

from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    inline_serializer,
)
from rest_framework import generics, status, viewsets
from rest_framework import serializers as drf_serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from users.authentication import BanAwareJWTAuthentication as JWTAuthentication
from users.email_service import EmailService
from users.models import User
from users.permissions import IsAdmin, IsSelfOrAdmin
from users.serializers import (
    ChangePasswordSerializer,
    MeUpdateSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserAdminSerializer,
    UserPublicSerializer,
    VerifyEmailConfirmSerializer,
)
from users.services import UserRegistrationService
from users.token_issuer import SimpleJWTTokenIssuer, TokenError
from users.tokens import (
    TokenInvalid,
    read_password_reset_token,
    read_verify_email_token,
)

logger = logging.getLogger(__name__)


@extend_schema(
    tags=["users"],
    summary="Register a new user",
    description=(
        "Creates a new user account. Privileged fields are stripped: only "
        "``email``, ``password``, ``first_name`` and ``last_name`` are "
        "honoured. Throttled under the ``register`` scope."
    ),
    request=RegisterSerializer,
    responses={201: UserPublicSerializer},
)
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
        return Response(UserPublicSerializer(user).data, status=status.HTTP_201_CREATED)


class MeView(APIView):
    """``/me/`` — get or partially update the current user's profile."""

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @extend_schema(
        tags=["users"],
        summary="Get the authenticated user's profile",
        responses={200: UserPublicSerializer},
    )
    def get(self, request):
        return Response(UserPublicSerializer(request.user).data)

    @extend_schema(
        tags=["users"],
        summary="Update the authenticated user's profile",
        description=(
            "Partial update — only the writable fields exposed by "
            "``MeUpdateSerializer`` are accepted."
        ),
        request=MeUpdateSerializer,
        responses={200: UserPublicSerializer},
    )
    def patch(self, request):
        serializer = MeUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserPublicSerializer(request.user).data)


class ChangePasswordView(APIView):
    """Change the password of the authenticated user."""

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @extend_schema(
        tags=["users"],
        summary="Change the authenticated user's password",
        description=(
            "Requires the current password (``old_password``) and a new "
            "one (``new_password``) which is run through Django's password "
            "validators. Returns ``204 No Content`` on success."
        ),
        request=ChangePasswordSerializer,
        responses={
            204: OpenApiResponse(description="Password updated."),
            400: OpenApiResponse(description="Validation failed."),
        },
    )
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

    @extend_schema(
        tags=["users"],
        summary="Log out by blacklisting a refresh token",
        description=(
            "Adds the supplied refresh token to the SimpleJWT blacklist so "
            "it can no longer be used to mint new access tokens. The "
            "client should also discard its locally-stored access token."
        ),
        request=inline_serializer(
            name="LogoutRequest",
            fields={
                "refresh": drf_serializers.CharField(
                    help_text="The refresh token to blacklist.",
                ),
            },
        ),
        responses={
            205: OpenApiResponse(description="Refresh token blacklisted."),
            400: OpenApiResponse(description="Missing or invalid refresh token."),
        },
    )
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


@extend_schema(tags=["users"])
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


class UserBanView(APIView):
    """Admin-only: ban or unban a user.

    ``POST /api/users/<id>/ban/``    — set ``is_banned=True``.
    ``POST /api/users/<id>/unban/``  — set ``is_banned=False``.
    Optional JSON body: ``{"reason": "..."}`` (informational, not stored
    server-side in MVP — surfaced in the response only).
    """

    permission_classes = [IsAuthenticated, IsAdmin]
    authentication_classes = [JWTAuthentication]

    @extend_schema(
        tags=["users"],
        summary="Ban or unban a user (admin)",
        description=(
            "Toggles the ``is_banned`` flag on the target user. The ``action`` "
            "URL kwarg is bound by the URL conf — there are two routes, "
            "``/users/<id>/ban/`` and ``/users/<id>/unban/`` — so callers "
            "never specify it in the body. ``reason`` is optional and is "
            "only echoed back in the response."
        ),
        parameters=[
            OpenApiParameter(
                name="id",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="Primary key of the target user.",
            ),
        ],
        request=inline_serializer(
            name="UserBanRequest",
            fields={
                "reason": drf_serializers.CharField(required=False, allow_blank=True),
            },
        ),
        responses={
            200: UserAdminSerializer,
            400: OpenApiResponse(description="Cannot ban yourself."),
            404: OpenApiResponse(description="User not found."),
        },
    )
    def post(self, request, pk: int, action: str):
        try:
            target = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if target == request.user:
            return Response(
                {"detail": "You cannot ban yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if action == "ban":
            target.is_banned = True
        elif action == "unban":
            target.is_banned = False
        else:  # pragma: no cover - URL conf restricts values
            return Response(
                {"detail": "Unknown action."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        target.save(update_fields=["is_banned"])
        return Response(UserAdminSerializer(target).data)


# ---------------------------------------------------------------------------
# Email verification + password reset
# ---------------------------------------------------------------------------


class VerifyEmailRequestView(APIView):
    """Re-send the verification email to the *currently authenticated* user.

    Throttled — must not be abused as a free email-sending oracle.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "email_verify"

    email_service = EmailService()

    @extend_schema(
        tags=["users"],
        summary="Resend verification email to the current user",
        request=None,
        responses={
            204: OpenApiResponse(description="Verification email sent (or already verified)."),
            503: OpenApiResponse(description="Email transport failure."),
        },
    )
    def post(self, request):
        user = request.user
        if user.is_verified:
            # Idempotent — nothing to do, but don't reveal extra info either.
            return Response(status=status.HTTP_204_NO_CONTENT)
        try:
            self.email_service.send_verify_email(user)
        except Exception:
            logger.exception("verify-email send failed for %s", user.email)
            return Response(
                {"detail": "Could not send the verification email."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class VerifyEmailConfirmView(APIView):
    """Public — confirms an email using a signed token."""

    permission_classes = [AllowAny]
    authentication_classes: list = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "email_verify"

    @extend_schema(
        tags=["users"],
        summary="Confirm an email-verification token",
        request=VerifyEmailConfirmSerializer,
        responses={
            200: UserPublicSerializer,
            400: OpenApiResponse(description="Invalid or expired token."),
        },
    )
    def post(self, request):
        serializer = VerifyEmailConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        try:
            user = read_verify_email_token(token)
        except TokenInvalid as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_verified:
            user.is_verified = True
            user.save(update_fields=["is_verified"])
        return Response(UserPublicSerializer(user).data)


class PasswordResetRequestView(APIView):
    """Public — emails a password-reset link if the address is registered.

    The response is identical regardless of whether the address exists, so
    the endpoint cannot be used as a user-enumeration oracle.
    """

    permission_classes = [AllowAny]
    authentication_classes: list = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset"

    email_service = EmailService()

    @extend_schema(
        tags=["users"],
        summary="Request a password-reset email",
        request=PasswordResetRequestSerializer,
        responses={
            204: OpenApiResponse(
                description=(
                    "Always 204 regardless of whether the address exists, "
                    "so the endpoint cannot be used for user enumeration."
                ),
            ),
        },
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            user = None
        if user is not None:
            try:
                self.email_service.send_password_reset_email(user)
            except Exception:
                # Log and swallow: surfacing transport errors here would
                # turn the endpoint back into an enumeration oracle.
                logger.exception("password-reset send failed for %s", email)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetConfirmView(APIView):
    """Public — completes a password reset using a signed token."""

    permission_classes = [AllowAny]
    authentication_classes: list = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset"

    @extend_schema(
        tags=["users"],
        summary="Confirm a password-reset token and set a new password",
        request=PasswordResetConfirmSerializer,
        responses={
            204: OpenApiResponse(description="Password updated."),
            400: OpenApiResponse(
                response=inline_serializer(
                    name="PasswordResetConfirmError",
                    fields={
                        "detail": drf_serializers.CharField(required=False),
                        "new_password": drf_serializers.ListField(
                            child=drf_serializers.CharField(), required=False
                        ),
                    },
                ),
                description="Invalid token or password validation failed.",
            ),
        },
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]
        try:
            user = read_password_reset_token(token)
        except TokenInvalid as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        # Re-run validators with the resolved user for similarity / common
        # checks; surface as a serializer-style field error.
        try:
            validate_password(new_password, user=user)
        except Exception as exc:  # django ValidationError
            messages = getattr(exc, "messages", [str(exc)])
            raise drf_serializers.ValidationError({"new_password": messages}) from exc
        user.set_password(new_password)
        user.save(update_fields=["password"])
        return Response(status=status.HTTP_204_NO_CONTENT)
