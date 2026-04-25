"""Signed, single-purpose, time-limited tokens for users-app email flows.

Wraps Django's built-in :class:`~django.core.signing.TimestampSigner` so we
get HMAC-signed tokens (tamper-proof) with a TTL — no extra dependency,
no DB row to revoke. Replay protection on top of the TTL is achieved
through *purpose binding* + a *salt component* derived from data that
changes when the action is consumed:

* ``verify-email`` tokens embed ``user.is_verified`` — once we flip the
  flag to ``True``, the *same* token decodes against a different salt and
  validation fails.
* ``password-reset`` tokens embed a hash of the current ``password`` field
  — once the password is changed, every previously-issued reset token for
  the same user becomes invalid.

The two purposes use distinct ``salt`` values, so a token issued for one
flow can never be presented to the other.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from django.conf import settings
from django.core import signing

from users.models import User

# Distinct salts isolate the two flows so cross-purpose use is impossible.
_VERIFY_EMAIL_SALT = "users.tokens.verify-email.v1"
_PASSWORD_RESET_SALT = "users.tokens.password-reset.v1"


class TokenInvalid(Exception):
    """Raised when a token is malformed, expired, or no longer valid."""


@dataclass(frozen=True)
class _Payload:
    user_id: int
    fingerprint: str  # state-bound string; mismatch ⇒ already-consumed.


def _password_fingerprint(user: User) -> str:
    # Only the first few bytes of the SHA-256 of the password hash. We never
    # expose the raw hash; the fingerprint is just enough to invalidate the
    # token once the password changes.
    raw = (user.password or "").encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _verify_fingerprint(user: User) -> str:
    # Single-character marker is enough: it flips when ``is_verified`` does.
    return "1" if user.is_verified else "0"


# ---------------------------------------------------------------------------
# Email verification
# ---------------------------------------------------------------------------


def make_verify_email_token(user: User) -> str:
    """Issue a signed token that confirms ``user``'s email address."""
    payload = {"uid": user.pk, "fp": _verify_fingerprint(user)}
    return signing.TimestampSigner(salt=_VERIFY_EMAIL_SALT).sign_object(payload)


def read_verify_email_token(token: str) -> User:
    """Validate a verify-email token and return the matching user.

    Raises :class:`TokenInvalid` for any failure (expired, tampered,
    already-consumed, unknown user).
    """
    max_age = settings.EMAIL_VERIFY_TOKEN_MAX_AGE
    try:
        payload = signing.TimestampSigner(salt=_VERIFY_EMAIL_SALT).unsign_object(
            token, max_age=max_age
        )
    except signing.SignatureExpired as exc:
        raise TokenInvalid("expired") from exc
    except signing.BadSignature as exc:
        raise TokenInvalid("invalid") from exc

    try:
        user = User.objects.get(pk=payload["uid"])
    except (KeyError, User.DoesNotExist) as exc:
        raise TokenInvalid("invalid") from exc

    if payload.get("fp") != _verify_fingerprint(user):
        # User is already verified — token has been consumed once.
        raise TokenInvalid("consumed")
    return user


# ---------------------------------------------------------------------------
# Password reset
# ---------------------------------------------------------------------------


def make_password_reset_token(user: User) -> str:
    """Issue a signed token that authorises a password change for ``user``."""
    payload = {"uid": user.pk, "fp": _password_fingerprint(user)}
    return signing.TimestampSigner(salt=_PASSWORD_RESET_SALT).sign_object(payload)


def read_password_reset_token(token: str) -> User:
    """Validate a password-reset token and return the matching user."""
    max_age = settings.PASSWORD_RESET_TOKEN_MAX_AGE
    try:
        payload = signing.TimestampSigner(salt=_PASSWORD_RESET_SALT).unsign_object(
            token, max_age=max_age
        )
    except signing.SignatureExpired as exc:
        raise TokenInvalid("expired") from exc
    except signing.BadSignature as exc:
        raise TokenInvalid("invalid") from exc

    try:
        user = User.objects.get(pk=payload["uid"])
    except (KeyError, User.DoesNotExist) as exc:
        raise TokenInvalid("invalid") from exc

    if payload.get("fp") != _password_fingerprint(user):
        # Password has changed since the token was issued — invalidate.
        raise TokenInvalid("consumed")
    return user


__all__ = [
    "TokenInvalid",
    "make_verify_email_token",
    "read_verify_email_token",
    "make_password_reset_token",
    "read_password_reset_token",
]
