"""Authentication classes for the users app.

Wraps :class:`rest_framework_simplejwt.authentication.JWTAuthentication` so
banned users are rejected even when they hold a valid (non-expired) token.
This keeps ban enforcement in a single, declarative place that every view
inherits via ``DEFAULT_AUTHENTICATION_CLASSES``.
"""

from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication


class BanAwareJWTAuthentication(JWTAuthentication):
    """JWTAuthentication subclass that rejects banned users."""

    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if getattr(user, "is_banned", False):
            raise exceptions.AuthenticationFailed(
                "This account has been banned.", code="user_banned"
            )
        return user
