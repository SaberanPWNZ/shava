from rest_framework import serializers

from reviews.models import Review
from reviews.choices import REVIEW_SCORE_CHOICES


class ReviewSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    place_name = serializers.CharField(source="place.name", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "place",
            "author",
            "score",
            "comment",
            "created_at",
            "is_moderated",
        ]
        read_only_fields = ["id", "author", "created_at", "is_moderated"]


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "place",
            "score",
            "comment",
        ]

    def validate_score(self, value):
        """Validate that score is within allowed choices"""
        valid_scores = [choice[0] for choice in REVIEW_SCORE_CHOICES]
        if value not in valid_scores:
            raise serializers.ValidationError("Invalid score value.")
        return value


class ReviewListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing reviews"""

    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "author_username",
            "score",
            "comment",
            "created_at",
        ]
