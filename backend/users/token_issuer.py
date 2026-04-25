"""Token issuance abstractions (DIP).

The views depend on the ``TokenIssuer`` protocol rather than directly on
SimpleJWT, so a future swap to OAuth/OIDC or a custom token backend does not
require changes to the views.
"""

from __future__ import annotations

from typing import Protocol

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


class TokenIssuer(Protocol):
    """Issue and revoke authentication tokens for a user."""

    def revoke_refresh_token(self, refresh_token: str) -> None:  # pragma: no cover
        ...


class SimpleJWTTokenIssuer:
    """Concrete ``TokenIssuer`` backed by ``rest_framework_simplejwt``."""

    def revoke_refresh_token(self, refresh_token: str) -> None:
        """Blacklist a refresh token. Raises :class:`TokenError` if invalid."""
        token = RefreshToken(refresh_token)  # type: ignore[arg-type]
        token.blacklist()


__all__ = ["TokenIssuer", "SimpleJWTTokenIssuer", "TokenError"]
