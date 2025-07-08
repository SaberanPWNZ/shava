from django.db import models


class Shwarma(models.Model):
    name = models.CharField(max_length=100)
    place = models.ForeignKey(
        "places.Place", on_delete=models.CASCADE, related_name="shwarmas"
    )
    description = models.TextField()
    ingredients = models.ManyToManyField("shwarma.Ingredient", related_name="shwarmas")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    main_image = models.ImageField(upload_to="shwarma_images/")
    additional_images = models.ManyToManyField(
        "shwarma.AdditionalImage", blank=True, related_name="shwarmas"
    )
