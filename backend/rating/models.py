from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# class UserRating(models.Model):
#     user = models.ForeignKey(
#         "users.User", related_name="ratings", on_delete=models.CASCADE
#     )
#     score = models.DecimalField(
#         max_digits=3,
#         decimal_places=2,
#         validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
#         help_text="Rating score between 0.0 and 10.0",
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     comment = models.TextField(
#         blank=True, null=True, help_text="Optional comment for the rating"
#     )
