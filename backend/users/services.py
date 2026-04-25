"""Application services for the users app.

Keeps business logic out of serializers/views (SRP) and provides a clear
seam for testing and future extension (e.g. sending verification emails,
emitting domain events).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from users.email_service import EmailService
from users.models import User

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RegistrationData:
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


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
        )
        # Dispatch the verification email through Celery so a slow SMTP
        # transport doesn't extend the registration response time. When
        # no broker is configured ``CELERY_TASK_ALWAYS_EAGER`` makes
        # this call synchronous, preserving the existing dev/test
        # behaviour where registration tests assert ``mail.outbox``.
        from users.tasks import send_verification_email

        try:
            send_verification_email.delay(user.pk)
        except Exception:  # pragma: no cover - already logged in the service.
            logger.warning(
                "Verification email could not be sent for %s; user can "
                "request a new one via /verify-email/request/.",
                user.email,
            )
        return user
