from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to="ingredient_images/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
