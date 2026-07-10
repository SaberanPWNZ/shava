"""In-app notifications.

One row per event per recipient. The row stores a machine ``type`` plus a
small ``data`` JSON payload (ids, names) — the frontend localises the
human-readable text itself, so the backend never bakes in a language.
"""

from django.conf import settings
from django.db import models


class Notification(models.Model):
    TYPE_REVIEW_APPROVED = "review_approved"
    TYPE_REVIEW_REJECTED = "review_rejected"
    TYPE_PLACE_APPROVED = "place_approved"
    TYPE_PLACE_REJECTED = "place_rejected"
    TYPE_REVIEW_REPLY = "review_reply"
    TYPE_FAVORITE_PLACE_REVIEW = "favorite_place_review"
    TYPE_BADGE_AWARDED = "badge_awarded"
    TYPE_CHOICES = [
        (TYPE_REVIEW_APPROVED, "Review approved"),
        (TYPE_REVIEW_REJECTED, "Review rejected"),
        (TYPE_PLACE_APPROVED, "Place approved"),
        (TYPE_PLACE_REJECTED, "Place rejected"),
        (TYPE_REVIEW_REPLY, "Reply to review"),
        (TYPE_FAVORITE_PLACE_REVIEW, "New review on a favorite place"),
        (TYPE_BADGE_AWARDED, "Badge awarded"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"{self.type} → {self.user_id}"
