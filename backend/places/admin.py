from django.contrib import admin
from places.models import Place


class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "district", "address", "created_at", "updated_at")
    search_fields = ("name", "district", "address")
    list_filter = ("district", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 20

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset


admin.site.register(Place, PlaceAdmin)
