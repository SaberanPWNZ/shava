"""Throttled login/refresh views that deliver tokens as HttpOnly cookies.

The token pair is still returned in the response body for non-browser
clients; browsers are expected to rely on the cookies only (the SPA never
persists tokens in JavaScript-accessible storage).
"""

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .cookies import REFRESH_COOKIE, clear_jwt_cookies, set_jwt_cookies
from .jwt_serializers import EmailTokenObtainPairSerializer


class EmailTokenObtainPairView(TokenObtainPairView):
    """Login endpoint with rate-limiting (``auth`` scope)."""

    serializer_class = EmailTokenObtainPairSerializer
    throttle_scope = "auth"

    def finalize_response(self, request, response, *args, **kwargs):
        if response.status_code == 200:
            set_jwt_cookies(
                response,
                access=response.data.get("access"),
                refresh=response.data.get("refresh"),
            )
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenRefreshView(TokenRefreshView):
    """Refresh that accepts the token from the body *or* the HttpOnly cookie."""

    def get_serializer(self, *args, **kwargs):
        data = kwargs.get("data")
        if data is not None and not data.get("refresh"):
            cookie_refresh = self.request.COOKIES.get(REFRESH_COOKIE)
            if cookie_refresh:
                kwargs["data"] = {**data, "refresh": cookie_refresh}
        return super().get_serializer(*args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        if response.status_code == 200:
            set_jwt_cookies(
                response,
                access=response.data.get("access"),
                refresh=response.data.get("refresh"),
            )
        elif response.status_code == 401:
            # The refresh token is invalid/blacklisted — drop stale cookies
            # so the browser stops retrying with them.
            clear_jwt_cookies(response)
        return super().finalize_response(request, response, *args, **kwargs)
