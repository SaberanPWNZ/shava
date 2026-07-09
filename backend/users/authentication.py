from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.cookies import ACCESS_COOKIE


class BanAwareJWTAuthentication(JWTAuthentication):
    """JWTAuthentication that rejects banned users.

    Accepts the access token from the ``Authorization: Bearer`` header
    (non-browser clients) or, when the header is absent, from the HttpOnly
    ``access_token`` cookie set at login (browser clients). CSRF exposure of
    the cookie path is mitigated by ``SameSite=Lax`` — see users/cookies.py.
    """

    def authenticate(self, request):
        if self.get_header(request) is None:
            raw_token = request.COOKIES.get(ACCESS_COOKIE)
            if raw_token is None:
                return None
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        return super().authenticate(request)

    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if getattr(user, "is_banned", False):
            raise exceptions.AuthenticationFailed(
                "This account has been banned.", code="user_banned"
            )
        return user
