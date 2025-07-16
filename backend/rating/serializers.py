from rest_framework import serializers
from .models import Achievement, UserRating, UserAchievement


class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for Achievement model."""

    class Meta:
        model = Achievement
        fields = [
            'id', 'name', 'description', 'icon', 'reviews_required',
            'created_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at']


class UserAchievementSerializer(serializers.ModelSerializer):
    """Serializer for UserAchievement model with achievement details."""
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = ['id', 'achievement', 'earned_at']
        read_only_fields = ['id', 'earned_at']


class UserRatingSerializer(serializers.ModelSerializer):
    """Serializer for UserRating model."""
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    achievements = UserAchievementSerializer(
        source='user.achievements', many=True, read_only=True
    )

    class Meta:
        model = UserRating
        fields = [
            'id', 'user_id', 'username', 'total_reviews',
            'average_score_given', 'level', 'experience_points',
            'achievements', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_id', 'username', 'total_reviews',
            'average_score_given', 'level', 'experience_points',
            'achievements', 'created_at', 'updated_at'
        ]


class UserRatingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating UserRating (admin only)."""

    class Meta:
        model = UserRating
        fields = [
            'user', 'total_reviews', 'average_score_given',
            'level', 'experience_points'
        ]
