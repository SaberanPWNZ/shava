from django.conf import settings
from django.db import models

from reviews.choices import REVIEW_SCORE_CHOICES


class Review(models.Model):
    place = models.ForeignKey(
        "places.Place", on_delete=models.CASCADE, related_name="review_set"
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.DecimalField(
        # 4 digits, not 3: the top choice "10.0" stored at 2 decimal places
        # is 10.00 — with max_digits=3 SQLite fails to even *read* the row.
        max_digits=4,
        decimal_places=2,
        choices=REVIEW_SCORE_CHOICES,
    )
    comment = models.TextField(blank=True, default="")
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
    updated_at = models.DateTimeField(auto_now=True)
    is_moderated = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Review by {self.author.username} - Rating: {self.score}"

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-created_at"]
        indexes = [
            # The public place page: approved reviews for one place.
            models.Index(fields=["place", "is_moderated", "is_deleted"]),
            # Profile pages and the review feed.
            models.Index(fields=["author", "-created_at"]),
        ]


class ReviewReply(models.Model):
    """A short public reply under a review — the "forum" part of the site.

    Replies are post-moderated (visible immediately, soft-deletable by the
    author or staff): requiring pre-moderation would kill conversations.
    """

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="replies")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="review_replies",
    )
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Review reply"
        verbose_name_plural = "Review replies"
        ordering = ["created_at"]
        indexes = [models.Index(fields=["review", "created_at"])]

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"Reply by {self.author_id} on review {self.review_id}"


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
