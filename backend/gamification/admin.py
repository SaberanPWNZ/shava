from django.contrib import admin

from .models import Badge, PointsTransaction, UserBadge, UserPointsBalance


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "tier", "points_reward", "is_active")
    list_filter = ("tier", "is_active")
    search_fields = ("code", "title")
    prepopulated_fields = {"code": ("title",)}


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ("user", "badge", "awarded_at")
    list_filter = ("badge",)
    search_fields = ("user__username", "user__email", "badge__code")
    readonly_fields = ("awarded_at",)


@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "reason", "ref_type", "ref_id", "created_at")
    list_filter = ("reason",)
    search_fields = ("user__username", "user__email")
    readonly_fields = ("user", "amount", "reason", "ref_type", "ref_id", "created_at")

    def has_add_permission(self, request):  # pragma: no cover - admin only
        return False

    def has_change_permission(self, request, obj=None):  # pragma: no cover
        return False


@admin.register(UserPointsBalance)
class UserPointsBalanceAdmin(admin.ModelAdmin):
    list_display = ("user", "total", "level", "updated_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("user", "total", "level", "updated_at")

    def has_add_permission(self, request):  # pragma: no cover
        return False

    def has_change_permission(self, request, obj=None):  # pragma: no cover
        return False
