from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("gamification", "0002_seed_badges"),
    ]

    operations = [
        migrations.AlterField(
            model_name="badge",
            name="tier",
            field=models.CharField(
                choices=[
                    ("bronze", "Bronze"),
                    ("silver", "Silver"),
                    ("gold", "Gold"),
                    ("platinum", "Platinum"),
                ],
                default="bronze",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="pointstransaction",
            name="reason",
            field=models.CharField(
                choices=[
                    ("REVIEW_CREATED", "Review created"),
                    ("REVIEW_FIRST_FOR_PLACE", "First review for place"),
                    ("REVIEW_PHOTO", "Review with dish photo"),
                    ("REVIEW_VERIFIED", "Review verified by moderator"),
                    ("REVIEW_HELPFUL_VOTE", "Review marked as helpful"),
                    ("REPLY_CREATED", "Reply posted under someone's review"),
                    ("RATING_CREATED", "Rated a place"),
                    ("PLACE_APPROVED", "Added place approved by moderators"),
                    ("BADGE_AWARDED", "Badge awarded"),
                    ("MANUAL_ADJUSTMENT", "Manual adjustment"),
                ],
                max_length=64,
            ),
        ),
    ]
