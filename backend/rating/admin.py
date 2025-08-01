from django.contrib import admin
from .models import Achievement, UserRating, UserAchievement


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'reviews_required', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('reviews_required', 'name')
    list_editable = ('is_active',)

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'icon', 'is_active')
        }),
        ('Criteria', {
            'fields': ('reviews_required',)
        }),
    )


@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'level', 'total_reviews', 'average_score_given',
        'experience_points', 'updated_at'
    )
    list_filter = ('level', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    ordering = ('-experience_points', '-level')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Statistics', {
            'fields': ('total_reviews', 'average_score_given')
        }),
        ('Progress', {
            'fields': ('level', 'experience_points')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_at')
    list_filter = ('achievement', 'earned_at')
    search_fields = ('user__username', 'user__email', 'achievement__name')
    ordering = ('-earned_at',)
    readonly_fields = ('earned_at',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('user', 'achievement')
        return self.readonly_fields
