from backend.places.models import Place
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
