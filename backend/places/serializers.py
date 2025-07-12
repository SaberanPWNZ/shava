from places.models import Place, PlaceRating
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


class PlaceSerializer(ModelSerializer):
    google_maps_url = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = "__all__"

    def get_google_maps_url(self, obj):
        if obj.latitude and obj.longitude:
            return f"https://www.google.com/maps/search/?api=1&query={obj.latitude},{obj.longitude}"
        return None


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
            "rating",
            "main_image",
            "additional_images",
            "website",
            "opening_hours",
            "is_featured",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["is_featured"] = False
        return Place.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def delete(self, instance):
        instance.delete()
        return instance


class PlaceRatingSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = PlaceRating
        fields = ["id", "user", "place", "rating", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        # Create or update the rating
        user = validated_data.get("user")
        place = validated_data.get("place")
        rating = validated_data.get("rating")

        place_rating, created = PlaceRating.objects.update_or_create(
            user=user,
            place=place,
            defaults={"rating": rating},
        )

        # Update the place's average rating
        place.update_rating()

        return place_rating
