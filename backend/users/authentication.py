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
