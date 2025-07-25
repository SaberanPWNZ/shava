from django.contrib import admin
from places.models import Place, PlaceRating


class PlaceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "district",
        "address",
        "status",
        "author",
        "moderated_by",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "district", "address", "author__username")
    list_filter = ("district", "status", "is_featured", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at", "rating", "moderated_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 20

    fieldsets = (
        (None, {"fields": ("name", "district", "address", "author")}),
        ("Location", {"fields": ("latitude", "longitude", "delivery")}),
        ("Content", {"fields": ("description", "main_image", "additional_images")}),
        ("Status & Rating", {"fields": ("status", "rating", "is_featured")}),
        (
            "Moderation",
            {"fields": ("moderated_by", "moderation_reason", "moderated_at")},
        ),
        ("Additional Info", {"fields": ("website", "opening_hours")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("author", "moderated_by")


class PlaceRatingAdmin(admin.ModelAdmin):
    list_display = ("place", "user", "rating", "created_at")
    search_fields = ("place__name", "user__username")
    list_filter = ("rating", "created_at")
    readonly_fields = ("created_at", "updated_at")


admin.site.register(Place, PlaceAdmin)
admin.site.register(PlaceRating, PlaceRatingAdmin)
