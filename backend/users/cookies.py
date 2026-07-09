"""HttpOnly JWT cookie helpers.

Tokens are delivered to browsers as ``HttpOnly`` cookies so they are
unreachable from JavaScript (XSS cannot exfiltrate them). ``SameSite=Lax``
means browsers do not attach them to cross-site POST/PUT/DELETE requests,
which is what makes cookie-based JWT auth safe without a separate CSRF
token for a JSON-only API.

Non-browser clients keep working: the login response body still carries
the token pair, and :class:`users.authentication.BanAwareJWTAuthentication`
accepts an ``Authorization: Bearer`` header before falling back to cookies.
"""

from django.conf import settings
from rest_framework.response import Response

ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"


def _cookie_kwargs(max_age: int) -> dict:
    return {
        "max_age": max_age,
        "httponly": True,
        "secure": settings.JWT_COOKIE_SECURE,
        "samesite": settings.JWT_COOKIE_SAMESITE,
        "path": "/",
    }


def set_jwt_cookies(
    response: Response, access: str | None = None, refresh: str | None = None
) -> None:
    """Attach whichever tokens are provided as HttpOnly cookies."""
    lifetimes = settings.SIMPLE_JWT
    if access:
        response.set_cookie(
            ACCESS_COOKIE,
            access,
            **_cookie_kwargs(int(lifetimes["ACCESS_TOKEN_LIFETIME"].total_seconds())),
        )
    if refresh:
        response.set_cookie(
            REFRESH_COOKIE,
            refresh,
            **_cookie_kwargs(int(lifetimes["REFRESH_TOKEN_LIFETIME"].total_seconds())),
        )


def clear_jwt_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_COOKIE, path="/")
    response.delete_cookie(REFRESH_COOKIE, path="/")
