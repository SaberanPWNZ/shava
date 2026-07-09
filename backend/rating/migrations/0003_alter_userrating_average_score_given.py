import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rating", "0002_alter_achievement_icon"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userrating",
            name="average_score_given",
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                help_text="Average score this user gives in reviews",
                max_digits=4,
                validators=[
                    django.core.validators.MinValueValidator(0.0),
                    django.core.validators.MaxValueValidator(10.0),
                ],
            ),
        ),
    ]
