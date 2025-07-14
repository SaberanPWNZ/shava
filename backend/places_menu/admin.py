from django.contrib import admin
from places_menu.models import Menu


class MenuAdmin(admin.ModelAdmin):
    list_display = ("name", "place", "item", "created_at", "updated_at", "description")
    search_fields = ("name", "place__name", "item__name")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 20
    autocomplete_fields = ["place", "item"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("place", "item")


admin.site.register(Menu, MenuAdmin)
