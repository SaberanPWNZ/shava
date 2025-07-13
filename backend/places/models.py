from django.db import models


# Create your models here.
class Place(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    delivery = models.BooleanField(default=False)
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.0
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
