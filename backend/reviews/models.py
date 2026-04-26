from django.conf import settings
from django.db import models

from reviews.choices import REVIEW_SCORE_CHOICES


class Review(models.Model):
    place = models.ForeignKey(
        "places.Place", on_delete=models.CASCADE, related_name="review_set"
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        choices=REVIEW_SCORE_CHOICES,
    )
    comment = models.TextField(blank=True, null=True)
    dish_image = models.ImageField(upload_to="review_dishes/", blank=True, null=True)
    receipt_image = models.ImageField(
        upload_to="review_receipts/", blank=True, null=True
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Set by a moderator after checking the receipt photo.",
    )
    helpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_moderated = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Review by {self.author.username} - Rating: {self.score}"

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-created_at"]


class ReviewHelpfulVote(models.Model):
    """A "this review was helpful" vote from one user on a review."""

    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="helpful_votes"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="helpful_votes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Review helpful vote"
        verbose_name_plural = "Review helpful votes"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["review", "user"], name="uniq_review_helpful_vote"
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"{self.user_id} ❤ {self.review_id}"
