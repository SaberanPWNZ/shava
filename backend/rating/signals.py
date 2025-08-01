from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from reviews.models import Review
from .models import UserRating, Achievement, UserAchievement


@receiver(post_save, sender=Review)
def update_user_rating_on_review_create(sender, instance, created, **kwargs):
    """Update user rating statistics when a review is created or updated."""
    if created or not created:  # Handle both create and update
        user = instance.author

        # Get or create user rating profile
        user_rating, _ = UserRating.objects.get_or_create(user=user)

        # Update statistics
        user_reviews = Review.objects.filter(author=user, is_deleted=False)
        user_rating.total_reviews = user_reviews.count()

        # Calculate average score given by user
        avg_score = user_reviews.aggregate(avg_score=Avg('score'))['avg_score']
        user_rating.average_score_given = avg_score or 0.0

        # Update experience points (simple system: 10 points per review)
        user_rating.experience_points = user_rating.total_reviews * 10

        # Update level (simple system: level = experience_points // 100 + 1)
        user_rating.level = max(1, user_rating.experience_points // 100 + 1)

        user_rating.save()

        # Check for new achievements only if review was created
        if created:
            check_and_award_achievements(user)


@receiver(post_delete, sender=Review)
def update_user_rating_on_review_delete(sender, instance, **kwargs):
    """Update user rating statistics when a review is deleted."""
    user = instance.author

    try:
        user_rating = UserRating.objects.get(user=user)

        # Update statistics
        user_reviews = Review.objects.filter(author=user, is_deleted=False)
        user_rating.total_reviews = user_reviews.count()

        # Calculate average score given by user
        avg_score = user_reviews.aggregate(avg_score=Avg('score'))['avg_score']
        user_rating.average_score_given = avg_score or 0.0

        # Update experience points
        user_rating.experience_points = user_rating.total_reviews * 10

        # Update level
        user_rating.level = max(1, user_rating.experience_points // 100 + 1)

        user_rating.save()

    except UserRating.DoesNotExist:
        pass


def check_and_award_achievements(user):
    """Check if user qualifies for new achievements and award them."""
    try:
        user_rating = UserRating.objects.get(user=user)
    except UserRating.DoesNotExist:
        return

    # Get all active achievements that user doesn't have yet
    existing_achievements = UserAchievement.objects.filter(
        user=user
    ).values_list('achievement_id', flat=True)
    available_achievements = Achievement.objects.filter(
        is_active=True
    ).exclude(id__in=existing_achievements)

    # Check each achievement
    for achievement in available_achievements:
        if user_rating.total_reviews >= achievement.reviews_required:
            # Award the achievement
            UserAchievement.objects.create(
                user=user,
                achievement=achievement
            )
