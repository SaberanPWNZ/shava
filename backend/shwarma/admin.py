from django.contrib import admin
from shwarma.models import Shwarma


class ShwarmaAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "price", "created_at", "updated_at")
    search_fields = ("name", "description")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 20

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset


admin.site.register(Shwarma, ShwarmaAdmin)
