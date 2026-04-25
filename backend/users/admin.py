from django.contrib import admin

from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_banned",
        "date_joined",
    )
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("is_staff", "is_active", "is_banned", "date_joined")
    readonly_fields = ("date_joined",)
    date_hierarchy = "date_joined"
    ordering = ("-date_joined",)
    list_per_page = 20
    actions = ("ban_users", "unban_users")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset

    @admin.action(description="Ban selected users")
    def ban_users(self, request, queryset):
        # Never ban the acting admin via bulk action.
        updated = queryset.exclude(pk=request.user.pk).update(is_banned=True)
        self.message_user(request, f"Banned {updated} user(s).")

    @admin.action(description="Unban selected users")
    def unban_users(self, request, queryset):
        updated = queryset.update(is_banned=False)
        self.message_user(request, f"Unbanned {updated} user(s).")


admin.site.register(User, UserAdmin)
