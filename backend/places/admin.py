from django.contrib import admin

from places.models import City, ModerationLog, Place, PlaceRating


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "region", "is_active", "created_at")
    list_filter = ("is_active", "region")
    search_fields = ("name", "slug", "region")
    ordering = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class PlaceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "city",
        "district",
        "address",
        "status",
        "author",
        "moderated_by",
        "created_at",
        "updated_at",
    )
    search_fields = ("name", "city", "district", "address", "author__username")
    list_filter = (
        "city",
        "district",
        "status",
        "is_featured",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at", "rating", "moderated_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 20

    fieldsets = (
        (
            None,
            {"fields": ("name", "city", "city_ref", "district", "address", "author")},
        ),
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


@admin.register(ModerationLog)
class ModerationLogAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "actor", "target_type", "target_id", "action")
    list_filter = ("target_type", "action")
    search_fields = ("actor__username", "reason")
    readonly_fields = ("actor", "target_type", "target_id", "action", "reason", "created_at")
    ordering = ("-created_at",)
