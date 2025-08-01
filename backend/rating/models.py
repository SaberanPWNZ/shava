from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Achievement(models.Model):
    """Model for defining different types of achievements users can earn."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="Icon class or emoji"
    )

    # Achievement criteria
    reviews_required = models.PositiveIntegerField(
        default=0,
        help_text="Number of reviews required to earn this achievement"
    )

    # Achievement metadata
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"
        ordering = ['reviews_required', 'name']

    def __str__(self):
        return f"{self.name} (Requires {self.reviews_required} reviews)"


class UserRating(models.Model):
    """Model to track user statistics and overall rating."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="rating_profile",
        on_delete=models.CASCADE
    )

    # User statistics
    total_reviews = models.PositiveIntegerField(default=0)
    average_score_given = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Average score this user gives in reviews"
    )

    # User level/rating
    level = models.PositiveIntegerField(default=1)
    experience_points = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Rating"
        verbose_name_plural = "User Ratings"
        ordering = ['-experience_points']

    def __str__(self):
        return (f"{self.user.username} - Level {self.level} "
                f"({self.total_reviews} reviews)")


class UserAchievement(models.Model):
    """Model to track which achievements users have earned."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="achievements",
        on_delete=models.CASCADE
    )
    achievement = models.ForeignKey(
        Achievement,
        related_name="earned_by",
        on_delete=models.CASCADE
    )
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Achievement"
        verbose_name_plural = "User Achievements"
        unique_together = ('user', 'achievement')
        ordering = ['-earned_at']

    def __str__(self):
        return f"{self.user.username} earned {self.achievement.name}"

