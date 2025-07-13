from django.db import models

from backend.shwarma.choices import ShwarmaSize


class AdditionalImage(models.Model):
    """Модель для додаткових зображень шаурми"""

    image = models.ImageField(upload_to="shwarma_additional_images/")

    def __str__(self):
        return f"Image {self.id}"


class Ingredient(models.Model):
    """Модель для інгредієнтів шаурми"""

    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to="ingredient_images/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Shwarma(models.Model):
    name = models.CharField(max_length=100)
    place = models.ForeignKey(
        "places.Place", on_delete=models.CASCADE, related_name="shwarmas"
    )
    description = models.TextField()
    size = models.CharField(
        max_length=50,
        choices=ShwarmaSize.choices
    )
    ingredients = models.ManyToManyField(
        "ingredients.Ingredient", related_name="shwarmas"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    main_image = models.ImageField(upload_to="shwarma_images/")
    additional_images = models.ManyToManyField(
        AdditionalImage, blank=True, related_name="shwarmas"
    )
    is_available = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    is_recommended = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.place.name}"

    class Meta:
        verbose_name = "Shwarma"
        verbose_name_plural = "Shwarmas"
        ordering = ["-created_at"]
