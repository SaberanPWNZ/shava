from rest_framework import serializers

from places_menu.models import Menu


class MenuItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)

    class Meta:
        model = Menu
        fields = [
            "id",
            "place",
            "name",
            "description",
            "price",
            "image",
            "category",
            "is_available",
            "item",
            "item_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "item_name", "place"]
