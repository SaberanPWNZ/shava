from rest_framework import serializers

from news.models import News


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = [
            "id",
            "title",
            "text",
            "published_date",
            "author",
            "image",
            "is_published",
        ]
        read_only_fields = ["id", "published_date"]
