from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from config.thumbnails import thumbnail_set
from places.models import City, ModerationLog, Place, PlaceRating


class CityMinimalSerializer(serializers.ModelSerializer):
    """Minimal, read-only city representation — used for the public
    ``/places/cities/`` list and embedded in user profile payloads."""

    class Meta:
        model = City
        fields = ["id", "name", "slug"]
        read_only_fields = fields


class PlaceSerializer(ModelSerializer):
    google_maps_url = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    stars = serializers.SerializerMethodField()
    ratings_count = serializers.SerializerMethodField()
    main_image_thumbnails = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

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
            "favorites_count",
            "is_favorited",
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

    def get_favorites_count(self, obj):
        annotated = getattr(obj, "_favorites_count", None)
        if annotated is not None:
            return annotated
        return obj.favorites.count()

    def get_is_favorited(self, obj) -> bool:
        """Whether the current viewer has bookmarked this place.

        Reads the per-request ``viewer_favorites`` prefetch (see
        :meth:`places.models.PlaceQuerySet.with_viewer_favorites`) when the
        view prepared it; falls back to a single EXISTS query on detail
        endpoints. Anonymous viewers always get ``False`` with no query.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None) if request is not None else None
        if user is None or not getattr(user, "is_authenticated", False):
            return False
        prefetched = getattr(obj, "viewer_favorites", None)
        if prefetched is not None:
            return len(prefetched) > 0
        return obj.favorites.filter(user_id=user.id).exists()

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
    viewer_rating = serializers.SerializerMethodField()
    viewer_review_id = serializers.SerializerMethodField()

    class Meta(PlaceSerializer.Meta):
        fields = PlaceSerializer.Meta.fields + [
            "ratings",
            "menu",
            "viewer_rating",
            "viewer_review_id",
        ]
        extra_kwargs = {
            "ratings": {"required": False},
        }
        read_only_fields = ["id", "created_at", "updated_at", "ratings", "menu"]

    def get_menu(self, obj):
        # Lazy import to avoid circular dependency at module load.
        from places_menu.serializers import MenuItemSerializer

        items = obj.menus.filter(is_available=True).order_by("category", "name")
        return MenuItemSerializer(items, many=True, context=self.context).data

    def _viewer(self):
        request = self.context.get("request")
        user = getattr(request, "user", None) if request is not None else None
        if user is None or not getattr(user, "is_authenticated", False):
            return None
        return user

    def get_viewer_rating(self, obj) -> float | None:
        """The viewer's own 1-5 star rating of this place, if any.

        Lets the UI render "your rating" instead of pretending the user
        never rated (ratings are stored on a 0-10 scale, hence the /2).
        """
        user = self._viewer()
        if user is None:
            return None
        # `ratings` is prefetched by the detail view — iterate in memory.
        for rating in obj.ratings.all():
            if rating.user_id == user.id:
                return float(rating.rating) / 2.0
        return None

    def get_viewer_review_id(self, obj) -> int | None:
        """Id of the viewer's (non-deleted) review of this place, if any.

        The UI uses it to swap the "write a review" form for a "you already
        reviewed this place" state instead of surfacing a 400 on submit.
        """
        user = self._viewer()
        if user is None:
            return None
        for review in obj.review_set.all():
            if review.author_id == user.id and not review.is_deleted:
                return review.id
        return None


class ModerationLogSerializer(ModelSerializer):
    """Read-only serializer for moderation audit-log entries."""

    actor_username = serializers.CharField(
        source="actor.username", read_only=True, default=""
    )

    class Meta:
        model = ModerationLog
        fields = [
            "id",
            "actor",
            "actor_username",
            "target_type",
            "target_id",
            "action",
            "reason",
            "created_at",
        ]
        read_only_fields = fields
