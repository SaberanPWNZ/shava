from rest_framework import serializers

from articles.models import Article
from config.thumbnails import thumbnail_set


def _cover_image_thumbnails(serializer, obj):
    request = serializer.context.get("request")
    return thumbnail_set(
        getattr(obj, "cover_image", None), alias_group="photo", request=request
    )


class ArticleListSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    cover_image_thumbnails = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "cover_image",
            "cover_image_thumbnails",
            "category",
            "author_name",
            "published_at",
            "is_published",
        ]
        read_only_fields = fields

    def get_author_name(self, obj):
        if not obj.author_id:
            return None
        return getattr(obj.author, "username", None) or getattr(
            obj.author, "email", None
        )

    def get_cover_image_thumbnails(self, obj):
        return _cover_image_thumbnails(self, obj)


class ArticleDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    cover_image_thumbnails = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "content",
            "cover_image",
            "cover_image_thumbnails",
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
        return getattr(obj.author, "username", None) or getattr(
            obj.author, "email", None
        )

    def get_cover_image_thumbnails(self, obj):
        return _cover_image_thumbnails(self, obj)
