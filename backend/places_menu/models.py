from django.db import models


MENU_CATEGORY_CHOICES = [
    ("shawarma", "Shawarma"),
    ("drinks", "Drinks"),
    ("sides", "Sides"),
    ("desserts", "Desserts"),
    ("other", "Other"),
]


class Menu(models.Model):
    name = models.CharField(max_length=200, default="Menu")
    place = models.ForeignKey(
        "places.Place", on_delete=models.CASCADE, related_name="menus"
    )
    item = models.ForeignKey(
        "shwarma.Shwarma",
        on_delete=models.SET_NULL,
        related_name="menus",
        null=True,
        blank=True,
    )
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, blank=True, null=True
    )
    image = models.ImageField(upload_to="menu_images/", blank=True, null=True)
    category = models.CharField(
        max_length=32, choices=MENU_CATEGORY_CHOICES, default="other"
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        if self.item_id:
            return f"{self.place.name} - {self.item.name}"
        return f"{self.place.name} - {self.name}"
