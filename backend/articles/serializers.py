from rest_framework import serializers

from articles.models import Article


class ArticleListSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "cover_image",
            "category",
            "author_name",
            "published_at",
            "is_published",
        ]
        read_only_fields = fields

    def get_author_name(self, obj):
        if not obj.author_id:
            return None
        return getattr(obj.author, "username", None) or getattr(obj.author, "email", None)


class ArticleDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "content",
            "cover_image",
            "category",
            "author",
            "author_name",
            "published_at",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at", "author_name"]

    def get_author_name(self, obj):
        if not obj.author_id:
            return None
        return getattr(obj.author, "username", None) or getattr(obj.author, "email", None)
