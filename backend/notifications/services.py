"""Tiny facade other apps call to emit a notification.

Kept as a function (not signals) so call sites stay explicit and greppable,
and so a failure to notify never breaks the calling transaction.
"""

import logging

from notifications.models import Notification

logger = logging.getLogger("notifications")


def notify(user, type_: str, **data) -> None:
    """Create an in-app notification; never raises toward the caller."""
    if user is None:
        return
    try:
        Notification.objects.create(user=user, type=type_, data=data)
    except Exception:  # pragma: no cover - defensive
        logger.exception("Failed to create notification %s for %s", type_, user)
