from places.models import Place, PlaceRating
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


class PlaceSerializer(ModelSerializer):
    google_maps_url = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = "__all__"

    def get_google_maps_url(self, obj):
        return obj.google_maps_url()

    def get_average_rating(self, obj):
        return obj.calculate_average_rating()

    def get_reviews_count(self, obj):
        return obj.review_set.count()


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
        # Remove rating from validated_data if present (should be calculated)
        validated_data.pop("rating", None)
        validated_data["is_featured"] = False
        validated_data["status"] = "On_moderation"
        return Place.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Remove rating from validated_data (should be calculated automatically)
        validated_data.pop("rating", None)
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

        # Update the place's average rating automatically
        place.update_rating()

        return place_rating
