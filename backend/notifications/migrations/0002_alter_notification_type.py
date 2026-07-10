from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="type",
            field=models.CharField(
                choices=[
                    ("review_approved", "Review approved"),
                    ("review_rejected", "Review rejected"),
                    ("place_approved", "Place approved"),
                    ("place_rejected", "Place rejected"),
                    ("review_reply", "Reply to review"),
                    ("favorite_place_review", "New review on a favorite place"),
                ],
                max_length=32,
            ),
        ),
    ]
