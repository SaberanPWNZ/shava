from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class Place(models.Model):
    name = (models.CharField(max_length=200),)
    address = models.CharField(max_length=300)
    delivery = models.BooleanField(default=False)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    description = models.TextField(blank=True, null=True)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal(0.0),
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
    )  # TODO add validators
    main_image = models.ImageField(upload_to="place_images/")
    additional_images = models.ImageField(
        upload_to="place_additional_images/", blank=True, null=True
    )
    shwarma = models.ManyToManyField(
        "shwarma.Shwarma", related_name="places", blank=True
    )
    reviews = models.ManyToManyField(
        "reviews.Review", related_name="places", blank=True
    )
    # videos #TODO add video field
