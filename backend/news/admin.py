from django.contrib import admin
from .models import News


class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "published_date")
    search_fields = ("title", "content")
    list_filter = ("published_date",)
    ordering = ("-published_date",)


admin.site.register(News, NewsAdmin)
