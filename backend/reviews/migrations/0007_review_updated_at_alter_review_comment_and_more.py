from django.db import migrations, models


def null_comments_to_empty(apps, schema_editor):
    Review = apps.get_model("reviews", "Review")
    Review.objects.filter(comment__isnull=True).update(comment="")


class Migration(migrations.Migration):
    dependencies = [
        ("places", "0009_placefavorite"),
        ("reviews", "0006_reviewreply"),
    ]

    operations = [
        migrations.RunPython(null_comments_to_empty, migrations.RunPython.noop),
        migrations.AddField(
            model_name="review",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="review",
            name="comment",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddIndex(
            model_name="review",
            index=models.Index(
                fields=["place", "is_moderated", "is_deleted"],
                name="reviews_rev_place_i_3ca06f_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="review",
            index=models.Index(
                fields=["author", "-created_at"],
                name="reviews_rev_author__8385c0_idx",
            ),
        ),
    ]
