from rest_framework import serializers

from reviews.choices import REVIEW_SCORE_CHOICES
from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    place_name = serializers.CharField(source="place.name", read_only=True)
    viewer_voted = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "place",
            "place_name",
            "author",
            "author_username",
            "score",
            "comment",
            "dish_image",
            "receipt_image",
            "is_verified",
            "helpful_count",
            "viewer_voted",
            "created_at",
            "is_moderated",
        ]
        read_only_fields = [
            "id",
            "author",
            "created_at",
            "is_moderated",
            "is_verified",
            "helpful_count",
            "viewer_voted",
        ]

    def get_viewer_voted(self, obj: Review) -> bool:
        """Whether the *current* request user has cast a helpful vote.

        Always ``False`` for anonymous viewers. Reads from a prefetched
        per-request attribute (``viewer_votes``) when the queryset has
        been prepared by the view — see
        :meth:`reviews.views.with_viewer_votes_prefetch` — so listing
        endpoints never trigger an N+1.
        """

        request = self.context.get("request")
        user = getattr(request, "user", None) if request is not None else None
        if user is None or not getattr(user, "is_authenticated", False):
            return False
        prefetched = getattr(obj, "viewer_votes", None)
        if prefetched is not None:
            return len(prefetched) > 0
        # Fallback for callers that don't prefetch (e.g. detail endpoints
        # building a serializer from a freshly-fetched ``Review`` instance).
        return obj.helpful_votes.filter(user_id=user.id).exists()


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "place",
            "score",
            "comment",
            "dish_image",
            "receipt_image",
        ]
        extra_kwargs = {
            # When the place is supplied via URL kwargs (nested route), the
            # client may omit the `place` field in the body.
            "place": {"required": False},
        }

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
