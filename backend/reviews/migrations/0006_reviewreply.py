from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("reviews", "0005_alter_review_score_max_digits"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReviewReply",
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
                ("text", models.TextField(max_length=1000)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="review_replies",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "review",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="replies",
                        to="reviews.review",
                    ),
                ),
            ],
            options={
                "verbose_name": "Review reply",
                "verbose_name_plural": "Review replies",
                "ordering": ["created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="reviewreply",
            index=models.Index(
                fields=["review", "created_at"], name="reviews_rev_review__d62646_idx"
            ),
        ),
    ]
