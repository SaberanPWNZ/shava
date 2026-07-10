from django.contrib import admin, messages

from places.models import ModerationLog
from reviews.models import Review, ReviewHelpfulVote
from reviews.services import notify_favoriters_of_new_review, notify_review_moderated


@admin.action(description="Mark selected reviews as verified")
def mark_verified(modeladmin, request, queryset):
    """Bulk action: flip ``is_verified`` False→True.

    Saves each instance individually so the ``pre_save``/``post_save``
    handlers in :mod:`gamification.signals` fire and award the
    ``REVIEW_VERIFIED`` bonus.
    """

    count = 0
    for review in queryset.filter(is_verified=False):
        review.is_verified = True
        review.save(update_fields=["is_verified"])
        count += 1
    modeladmin.message_user(
        request, f"Verified {count} review(s).", level=messages.SUCCESS
    )


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "place",
        "author",
        "score",
        "created_at",
        "is_moderated",
        "is_verified",
        "helpful_count",
    )
    search_fields = ("place__name", "author__username", "comment")
    list_filter = (
        "score",
        "is_moderated",
        "is_verified",
        "is_deleted",
        "created_at",
    )
    readonly_fields = ("created_at", "helpful_count")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 20
    actions = [mark_verified]

    def save_model(self, request, obj, form, change):
        previous = None
        if change:
            previous = (
                Review.objects.filter(pk=obj.pk)
                .values("is_moderated", "is_deleted")
                .first()
            )
        super().save_model(request, obj, form, change)

        was_pending = (
            previous and not previous["is_moderated"] and not previous["is_deleted"]
        )
        if not was_pending:
            return

        if obj.is_moderated and not obj.is_deleted:
            action = "approve"
        elif obj.is_deleted and not obj.is_moderated:
            action = "reject"
        else:
            return

        if obj.place_id:
            obj.place.recalculate_rating_from_reviews()

        ModerationLog.objects.create(
            actor=request.user,
            target_type=ModerationLog.TARGET_REVIEW,
            target_id=obj.id,
            action=action,
        )
        notify_review_moderated(obj, action)
        if action == "approve":
            notify_favoriters_of_new_review(obj)


admin.site.register(Review, ReviewAdmin)


@admin.register(ReviewHelpfulVote)
class ReviewHelpfulVoteAdmin(admin.ModelAdmin):
    list_display = ("review", "user", "created_at")
    search_fields = ("review__id", "user__username")
    readonly_fields = ("created_at",)
