"""Seed the initial badge catalogue.

Idempotent — uses ``update_or_create`` so re-running the migration on
an existing database is safe.
"""

from django.db import migrations


SEED_BADGES = [
    {
        "code": "first_review",
        "title": "First Review",
        "description": "Posted your very first review.",
        "icon": "🥇",
        "tier": "bronze",
        "points_reward": 0,
    },
    {
        "code": "ten_reviews",
        "title": "Ten Reviews",
        "description": "Posted ten reviews. You're a regular!",
        "icon": "📝",
        "tier": "silver",
        "points_reward": 25,
    },
    {
        "code": "foodie",
        "title": "Foodie",
        "description": "Reached the Foodie level (50 points).",
        "icon": "🍽️",
        "tier": "bronze",
        "points_reward": 0,
    },
    {
        "code": "verified_five",
        "title": "Verified Five",
        "description": "Five of your reviews were verified by moderators.",
        "icon": "✅",
        "tier": "silver",
        "points_reward": 50,
    },
    {
        "code": "helpful_fifty",
        "title": "Helpful 50",
        "description": "Other users marked your reviews as helpful 50 times.",
        "icon": "👍",
        "tier": "gold",
        "points_reward": 100,
    },
]


def seed_badges(apps, schema_editor):
    Badge = apps.get_model("gamification", "Badge")
    for entry in SEED_BADGES:
        Badge.objects.update_or_create(code=entry["code"], defaults=entry)


def unseed_badges(apps, schema_editor):
    Badge = apps.get_model("gamification", "Badge")
    Badge.objects.filter(code__in=[b["code"] for b in SEED_BADGES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("gamification", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_badges, unseed_badges),
    ]
