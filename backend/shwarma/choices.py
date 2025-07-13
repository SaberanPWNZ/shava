from django.db import models


class ShwarmaSize(models.TextChoices):
    MINI = "S", "Mini"
    STANDART = "M", "Stardart"
    LARGE = "L", "Large"
    XXLARGE = "XL", "Extra Large"
