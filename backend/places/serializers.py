from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from config.thumbnails import thumbnail_set
from places.models import Place, PlaceRating


class PlaceSerializer(ModelSerializer):
    google_maps_url = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    stars = serializers.SerializerMethodField()
    ratings_count = serializers.SerializerMethodField()
    main_image_thumbnails = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = [
            "id",
            "name",
            "city",
            "city_ref",
            "district",
            "address",
            "delivery",
            "latitude",
            "longitude",
            "description",
            "status",
            "rating",
            "stars",
            "ratings_count",
            "main_image",
            "main_image_thumbnails",
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

    def get_main_image_thumbnails(self, obj):
        return thumbnail_set(
            obj.main_image, alias_group="photo", request=self.context.get("request")
        )

    def get_google_maps_url(self, obj):
        return obj.google_maps_url()

    def get_average_rating(self, obj):
        annotated = getattr(obj, "_avg_rating", None)
        if annotated is not None:
            return annotated
        return obj.calculate_average_rating()

    def get_reviews_count(self, obj):
        annotated = getattr(obj, "_reviews_count", None)
        if annotated is not None:
            return annotated
        try:
            return obj.review_set.filter(is_moderated=True, is_deleted=False).count()
        except Exception:
            return 0

    def get_stars(self, obj):
        return obj.stars

    def get_ratings_count(self, obj):
        annotated = getattr(obj, "_ratings_count", None)
        if annotated is not None:
            return annotated
        return obj.ratings_count


class PlaceCreateSerializer(ModelSerializer):
    # Coordinates and city are mandatory at creation time so each new place
    # has a city and a map point per product spec.
    city = serializers.CharField(required=True, allow_blank=False, max_length=100)
    latitude = serializers.DecimalField(
        required=True,
        allow_null=False,
        max_digits=9,
        decimal_places=6,
        min_value=-90,
        max_value=90,
    )
    longitude = serializers.DecimalField(
        required=True,
        allow_null=False,
        max_digits=9,
        decimal_places=6,
        min_value=-180,
        max_value=180,
    )

    class Meta:
        model = Place
        fields = [
            "name",
            "city",
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
            "city",
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
    menu = serializers.SerializerMethodField()

    class Meta(PlaceSerializer.Meta):
        fields = PlaceSerializer.Meta.fields + ["ratings", "menu"]
        extra_kwargs = {
            "ratings": {"required": False},
        }
        read_only_fields = ["id", "created_at", "updated_at", "ratings", "menu"]

    def get_menu(self, obj):
        # Lazy import to avoid circular dependency at module load.
        from places_menu.serializers import MenuItemSerializer

        items = obj.menus.filter(is_available=True).order_by("category", "name")
        return MenuItemSerializer(items, many=True, context=self.context).data
