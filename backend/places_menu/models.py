from django.db import models


class Menu(models.Model):
    name = models.CharField(max_length=200, default="Menu")
    place = models.ForeignKey(
        "places.Place", on_delete=models.CASCADE, related_name="menus"
    )
    item = models.ForeignKey(
        "shwarma.Shwarma", on_delete=models.CASCADE, related_name="menus"
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.place.name} - {self.item.name}"
