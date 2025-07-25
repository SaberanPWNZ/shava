from places.models import Place, PlaceRating
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from moderation.models import ModeratedObject


class PlaceSerializer(ModelSerializer):
    google_maps_url = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = [
            "id",
            "name",
            "district",
            "address",
            "delivery",
            "latitude",
            "longitude",
            "description",
            "status",
            "rating",
            "main_image",
            "additional_images",
            "created_at",
            "updated_at",
            "website",
            "opening_hours",
            "is_featured",
            "author",
            "moderated_by",
            "moderation_reason",
            "moderated_at",
            "google_maps_url",
            "average_rating",
            "reviews_count",
        ]

    def get_google_maps_url(self, obj):
        return obj.google_maps_url()

    def get_average_rating(self, obj):
        return obj.calculate_average_rating()

    def get_reviews_count(self, obj):
        return (
            getattr(obj, "review_set", obj.reviews).count()
            if hasattr(obj, "review_set") or hasattr(obj, "reviews")
            else 0
        )


class PlaceCreateSerializer(ModelSerializer):
    class Meta:
        model = Place
        fields = [
            "name",
            "address",
            "delivery",
            "latitude",
            "longitude",
            "description",
            "main_image",
            "additional_images",
            "website",
            "opening_hours",
        ]
        read_only_fields = [
            "created_at",
            "updated_at",
            "rating",
            "is_featured",
            "status",
        ]

    def create(self, validated_data):
        validated_data.pop("rating", None)
        validated_data["is_featured"] = False
        validated_data["status"] = "On_moderation"
        return Place.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("rating", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PlaceUpdateSerializer(ModelSerializer):
    address = serializers.CharField(required=False)
    main_image = serializers.ImageField(required=False)

    class Meta:
        model = Place
        fields = [
            "name",
            "district",
            "address",
            "delivery",
            "latitude",
            "longitude",
            "description",
            "main_image",
            "additional_images",
            "website",
            "opening_hours",
            "status",
        ]
        read_only_fields = ["created_at", "updated_at", "rating", "is_featured"]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PlaceRatingSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PlaceRating
        fields = ["id", "user", "place", "rating", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        user = validated_data.get("user")
        place = validated_data.get("place")
        rating_value = validated_data.get("rating")

        place_rating, created = PlaceRating.objects.update_or_create(
            user=user,
            place=place,
            defaults={"rating": rating_value},
        )

        place.update_rating()

        return place_rating

    def update(self, instance, validated_data):
        instance.rating = validated_data.get("rating", instance.rating)
        instance.save()

        instance.place.update_rating()

        return instance


class PlaceDetailSerializer(PlaceSerializer):
    ratings = PlaceRatingSerializer(many=True, read_only=True)

    class Meta(PlaceSerializer.Meta):
        fields = PlaceSerializer.Meta.fields + ["ratings"]
        extra_kwargs = {
            "ratings": {"required": False},
        }


class PlaceModerationSerializer(serializers.ModelSerializer):
    """Serializer for moderated places"""

    object_data = serializers.SerializerMethodField()
    content_object = serializers.SerializerMethodField()

    class Meta:
        model = ModeratedObject
        fields = [
            "id",
            "object_pk",
            "moderation_status",
            "moderated_by",
            "moderation_date",
            "moderation_reason",
            "date_created",
            "object_data",
            "content_object",
        ]

    def get_object_data(self, obj):
        """Get the actual place data"""
        if obj.content_object:
            return PlaceCreateSerializer(obj.content_object).data
        return None

    def get_content_object(self, obj):
        """Get basic info about the content object"""
        if obj.content_object:
            return {
                "name": obj.content_object.name,
                "address": obj.content_object.address,
                "author": obj.content_object.author.username
                if obj.content_object.author
                else None,
            }
        return None
