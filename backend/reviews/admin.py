from django.contrib import admin
from reviews.models import Review


class ReviewAdmin(admin.ModelAdmin):
    list_display = ("place", "author", "score", "created_at", "is_moderated")
    search_fields = ("place__name", "author__username", "comment")
    list_filter = ("score", "is_moderated", "is_deleted", "created_at")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 20


admin.site.register(Review, ReviewAdmin)
