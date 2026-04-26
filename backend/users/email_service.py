"""Email-driven account flows: verification + password reset.

Templates live in ``users/templates/users/email/`` (UA-language).
The actual transport is configured by ``settings.EMAIL_BACKEND`` — defaults
to the console backend so a fresh VPS install works without SMTP.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from users.models import User
from users.tokens import (
    make_password_reset_token,
    make_verify_email_token,
)

logger = logging.getLogger(__name__)


def _frontend_link(path: str) -> str:
    """Build an absolute frontend URL from a relative ``path``."""
    return f"{settings.FRONTEND_URL.rstrip('/')}{path}"


def _render_subject(template_name: str, context: dict) -> str:
    # Subject must be a single line with no trailing newline.
    return render_to_string(template_name, context).strip().splitlines()[0]


class EmailService:
    """Sends transactional emails for the users app.

    Kept as a class (rather than module-level functions) so tests can swap
    in a fake via ``override_settings(EMAIL_BACKEND=...)`` *or* by
    monkeypatching the instance.
    """

    def send_verify_email(self, user: User) -> None:
        token = make_verify_email_token(user)
        ctx = {
            "user": user,
            "verify_url": _frontend_link(f"/verify-email/{token}"),
            "ttl_hours": max(1, settings.EMAIL_VERIFY_TOKEN_MAX_AGE // 3600),
        }
        subject = _render_subject("users/email/verify_email_subject.txt", ctx)
        body = render_to_string("users/email/verify_email_body.txt", ctx)
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception:  # pragma: no cover - transport errors are logged.
            # Never let email failures break the surrounding HTTP request:
            # registration / verify-email-request views wrap this call but
            # we also defend in depth in case a future caller forgets to.
            logger.exception("Failed to send verification email to %s", user.email)
            raise

    def send_password_reset_email(self, user: User) -> None:
        token = make_password_reset_token(user)
        ctx = {
            "user": user,
            "reset_url": _frontend_link(f"/reset-password/{token}"),
            "ttl_hours": max(1, settings.PASSWORD_RESET_TOKEN_MAX_AGE // 3600),
        }
        subject = _render_subject("users/email/password_reset_subject.txt", ctx)
        body = render_to_string("users/email/password_reset_body.txt", ctx)
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception:  # pragma: no cover - transport errors are logged.
            logger.exception("Failed to send password-reset email to %s", user.email)
            raise


__all__ = ["EmailService"]
