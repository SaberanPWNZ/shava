"""Celery tasks for the users app.

Exposes thin wrappers around :class:`users.email_service.EmailService`
so transactional emails can be dispatched off the request thread when a
broker is configured. When no broker is configured ``settings``
auto-flips :data:`CELERY_TASK_ALWAYS_EAGER` so ``.delay()`` runs the
task synchronously inside the calling process — this is what the test
suite and CI rely on.

Each task accepts a primary key and re-fetches the user, never the
``User`` instance itself: pickling ORM objects across process
boundaries is fragile and tasks must always work against the current DB
state.
"""

from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name="users.send_verification_email",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=3,
)
def send_verification_email(user_id: int) -> None:
    """Send a verification email to ``user_id`` if the user still exists."""

    from users.email_service import EmailService
    from users.models import User

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.info(
            "send_verification_email: user %s no longer exists; dropping task",
            user_id,
        )
        return
    EmailService().send_verify_email(user)


@shared_task(
    name="users.send_password_reset_email",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=3,
)
def send_password_reset_email(user_id: int) -> None:
    """Send a password-reset email to ``user_id`` if the user still exists."""

    from users.email_service import EmailService
    from users.models import User

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.info(
            "send_password_reset_email: user %s no longer exists; dropping task",
            user_id,
        )
        return
    EmailService().send_password_reset_email(user)
