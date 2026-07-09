"""Application services for the users app.

Keeps business logic out of serializers/views (SRP) and provides a clear
seam for testing and future extension (e.g. sending verification emails,
emitting domain events).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from users.models import User
from users.serivces.email_service import EmailService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RegistrationData:
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: str = ""
    city_id: Optional[int] = None
    marketing_opt_in: bool = False
    terms_accepted_at: Optional[datetime] = None


class UserRegistrationService:
    """Creates regular users.

    The service is the *only* place that creates users from the public API,
    which guarantees that no privileged flag (``is_staff``, ``is_admin``,
    ``is_superuser``, ``is_moderator``, ``is_verified``) can ever be set via
    public input — preventing privilege-escalation regardless of what the
    serializer accepts.

    Also dispatches the post-registration verification email; failures are
    logged but never propagated, so a transient SMTP outage does not break
    a user's registration. The user can request a fresh verification email
    later via the dedicated endpoint.
    """

    def __init__(self, email_service: EmailService | None = None) -> None:
        self._email_service = email_service or EmailService()

    def register(self, data: RegistrationData) -> User:
        user = User.objects.create_user(
            email=data.email,
            password=data.password,
            first_name=data.first_name or "",
            last_name=data.last_name or "",
            phone=data.phone or "",
            city_id=data.city_id,
            marketing_opt_in=data.marketing_opt_in,
            terms_accepted_at=data.terms_accepted_at,
        )
        from users.tasks import send_verification_email

        try:
            send_verification_email.delay(user.pk)
        except Exception:
            logger.warning(
                "Verification email could not be sent for %s; user can "
                "request a new one via /verify-email/request/.",
                user.email,
            )
        return user


class AccountDeletionService:
    """Soft-deletes (deactivates + anonymizes) a user's own account.

    Never hard-deletes: places, reviews, ratings and points transactions
    authored by the user must survive so aggregate data (place ratings,
    leaderboards, moderation history) stays correct and FK integrity is
    never at risk. Anonymizing the identifying fields plus deactivating the
    account and revoking every outstanding refresh token is enough to
    honor a "delete my account" request without a cascading-delete blast
    radius.
    """

    def delete(self, user: User) -> None:
        from rest_framework_simplejwt.token_blacklist.models import (
            BlacklistedToken,
            OutstandingToken,
        )

        for outstanding in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=outstanding)

        user.email = f"deleted-user-{user.pk}@shava.invalid"
        user.username = f"deleted-user-{user.pk}"
        user.first_name = ""
        user.last_name = ""
        user.phone = ""
        user.bio = ""
        user.avatar = None
        user.city = None
        user.telegram_id = None
        user.marketing_opt_in = False
        user.is_active = False
        user.set_unusable_password()
        user.save()
