from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.utils import timezone

from places.choices import DISTRICT_CHOICES, PLACE_STATUS_CHOICES

User = get_user_model()


class City(models.Model):
    """A reference catalog of cities a `Place` can belong to.

    Existing places carry a free-text ``Place.city`` value; the new
    :class:`Place.city_ref` FK points to a row in this table when known
    so we can filter on a clean primary key (``?city=<slug-or-id>``)
    without losing the original string for legacy rows.
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    region = models.CharField(max_length=100, blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return self.name


class PlaceRating(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="place_ratings"
    )
    place = models.ForeignKey("Place", on_delete=models.CASCADE, related_name="ratings")
    rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "place")
        verbose_name = "Place Rating"
        verbose_name_plural = "Place Ratings"

    def __str__(self):
        return f"{self.place.name} - {self.rating}"


class Place(models.Model):
    name = models.CharField(max_length=200, default="Unnamed Place")
    city = models.CharField(max_length=100, default="Київ")
    city_ref = models.ForeignKey(
        "City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="places",
        help_text=(
            "Optional reference to the canonical City row. The free-text "
            "`city` field above is preserved for legacy/back-compat reads."
        ),
    )
    district = models.CharField(
        max_length=100, choices=DISTRICT_CHOICES, default="Unknown"
    )
    address = models.CharField(max_length=300)
    delivery = models.BooleanField(default=False)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    reviews_count = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=50, choices=PLACE_STATUS_CHOICES, default="On_moderation"
    )
    rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal(0.0),
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Average rating calculated from reviews",
    )
    main_image = models.ImageField(upload_to="place_images/")
    additional_images = models.ImageField(
        upload_to="place_additional_images/", blank=True, null=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    website = models.URLField(blank=True, null=True)
    opening_hours = models.CharField(max_length=100, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_places",
        null=True,
        blank=True,
    )
    moderated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moderated_places",
    )
    moderation_reason = models.TextField(blank=True, null=True)
    moderated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Place"
        verbose_name_plural = "Places"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def calculate_average_rating(self):
        """Calculate the average rating from PlaceRating objects."""
        avg = self.ratings.aggregate(avg_rating=Avg("rating"))["avg_rating"]
        return avg if avg is not None else Decimal("0.0")

    def update_rating(self):
        """Update the rating field with the calculated average from PlaceRating objects."""
        self.rating = self.calculate_average_rating()
        self.save(update_fields=["rating"])

    def recalculate_rating_from_reviews(self):
        """Recompute the rating from approved (moderated, not deleted) reviews.

        Uses the lazy import to avoid circular imports at module load time.
        Reviews use a 1-10 score, matching the place rating scale.
        """
        from reviews.models import Review
        from django.db.models import Avg

        avg = Review.objects.filter(
            place=self, is_moderated=True, is_deleted=False
        ).aggregate(avg=Avg("score"))["avg"]
        self.rating = avg if avg is not None else Decimal("0.0")
        self.save(update_fields=["rating"])
        return self.rating

    def google_maps_url(self):
        if self.latitude and self.longitude:
            return f"https://www.google.com/maps/search/?api=1&query={self.latitude},{self.longitude}"
        return None

    def approve(self, moderator, reason=""):
        """Approve the place"""
        self.status = "Active"
        self.moderated_by = moderator
        self.moderation_reason = reason
        self.moderated_at = timezone.now()
        self.save()

    def reject(self, moderator, reason=""):
        """Reject the place"""
        self.status = "Inactive"
        self.moderated_by = moderator
        self.moderation_reason = reason
        self.moderated_at = timezone.now()
        self.save()

    @property
    def stars(self):
        """0-5 star representation derived from the 0-10 stored rating."""
        try:
            return round(float(self.rating) / 2.0, 1)
        except (TypeError, ValueError):
            return 0.0

    @property
    def ratings_count(self):
        return self.ratings.count()
