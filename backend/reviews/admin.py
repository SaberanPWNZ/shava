from django.contrib import admin, messages
from reviews.models import Review, ReviewHelpfulVote


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


admin.site.register(Review, ReviewAdmin)


@admin.register(ReviewHelpfulVote)
class ReviewHelpfulVoteAdmin(admin.ModelAdmin):
    list_display = ("review", "user", "created_at")
    search_fields = ("review__id", "user__username")
    readonly_fields = ("created_at",)
