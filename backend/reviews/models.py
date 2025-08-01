from django.db import models
from django.conf import settings
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
    created_at = models.DateTimeField(auto_now_add=True)
    is_moderated = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Review by {self.author.username} - Rating: {self.score}"

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-created_at"]
