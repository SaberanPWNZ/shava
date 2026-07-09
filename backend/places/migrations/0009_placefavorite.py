from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("places", "0008_moderationlog"),
    ]

    operations = [
        migrations.CreateModel(
            name="PlaceFavorite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "place",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorites",
                        to="places.place",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="favorite_places",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Place favorite",
                "verbose_name_plural": "Place favorites",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="placefavorite",
            constraint=models.UniqueConstraint(
                fields=("user", "place"), name="uniq_place_favorite"
            ),
        ),
    ]
