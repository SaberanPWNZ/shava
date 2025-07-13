from rest_framework import serializers
from places.models import Place


class PlaceSerializer(serializers.ModelSerializer):
    """Serializer for Place model"""

    class Meta:
        model = Place
        fields = [
            "id",
            "name",
            "address", 
            "delivery",
            "rating",
            "main_image",
            "additional_images",
        ]
        read_only_fields = ["id", "rating"]

    def validate_name(self, value):
        """Validate that name is not empty"""
        if not value or value.strip() == "":
            raise serializers.ValidationError("Name cannot be empty")
        return value.strip()

    def validate_address(self, value):
        """Validate that address is not empty"""
        if not value or value.strip() == "":
            raise serializers.ValidationError("Address cannot be empty")
        return value.strip()