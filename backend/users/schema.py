"""drf-spectacular extension for ``BanAwareJWTAuthentication``.

drf-spectacular ships with a ready-made extension for SimpleJWT's
``JWTAuthentication`` (under ``drf_spectacular.contrib.rest_framework_simplejwt``)
but it only matches the *exact* class — our :class:`BanAwareJWTAuthentication`
subclass therefore wasn't picked up, and every endpoint emitted a
"could not resolve authenticator" warning. Subclassing the existing
extension is the documented fix and makes the schema declare ``bearerAuth``
on every protected operation.
"""

from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme


class BanAwareJWTScheme(SimpleJWTScheme):
    """Reuse the SimpleJWT bearer-auth security scheme for our subclass."""

    target_class = "users.authentication.BanAwareJWTAuthentication"
    name = "jwtAuth"


__all__ = ["BanAwareJWTScheme"]
