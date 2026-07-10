from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("places", "0009_placefavorite"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="place",
            name="additional_images",
        ),
        migrations.RemoveField(
            model_name="place",
            name="reviews_count",
        ),
        migrations.AddField(
            model_name="place",
            name="instagram",
            field=models.URLField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="place",
            name="phone",
            field=models.CharField(blank=True, default="", max_length=32),
        ),
        migrations.AddField(
            model_name="place",
            name="price_level",
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[
                    (1, "₴ — budget"),
                    (2, "₴₴ — mid-range"),
                    (3, "₴₴₴ — premium"),
                ],
                null=True,
            ),
        ),
        migrations.CreateModel(
            name="PlaceImage",
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
                ("image", models.ImageField(upload_to="place_gallery/")),
                ("caption", models.CharField(blank=True, default="", max_length=200)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "place",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="places.place",
                    ),
                ),
            ],
            options={
                "verbose_name": "Place image",
                "verbose_name_plural": "Place images",
                "ordering": ["sort_order", "id"],
            },
        ),
    ]
