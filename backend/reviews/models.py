from django.db import models


class Review(models.Model):
    author = models.ForeignKey("user.User", on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=3, decimal_places=2)  # TODO ADD VALIDATION
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_moderated = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Review by {self.author.name} - Rating: {self.score}"

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-created_at"]
