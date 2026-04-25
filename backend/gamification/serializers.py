"""Serializers for the gamification HTTP API.

Each serializer is intentionally narrow (ISP): we don't reuse a single
``UserGamificationSerializer`` for every response.
"""

from __future__ import annotations

from rest_framework import serializers

from .levels import level_for
from .models import Badge, PointsTransaction, UserBadge, UserPointsBalance


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ["code", "title", "description", "icon", "tier", "points_reward"]


class UserBadgeSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source="badge.code", read_only=True)
    title = serializers.CharField(source="badge.title", read_only=True)
    description = serializers.CharField(source="badge.description", read_only=True)
    icon = serializers.CharField(source="badge.icon", read_only=True)
    tier = serializers.CharField(source="badge.tier", read_only=True)

    class Meta:
        model = UserBadge
        fields = ["code", "title", "description", "icon", "tier", "awarded_at"]


class PointsTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointsTransaction
        fields = ["id", "amount", "reason", "ref_type", "ref_id", "created_at"]


class _LevelMixin(serializers.Serializer):
    """Adds level-derived read-only fields to a serializer payload."""

    level = serializers.SerializerMethodField()
    level_title = serializers.SerializerMethodField()
    next_threshold = serializers.SerializerMethodField()
    progress_pct = serializers.SerializerMethodField()

    def _level_info(self, obj):
        total = getattr(obj, "total", 0) or 0
        return level_for(int(total))

    def get_level(self, obj):
        return self._level_info(obj).level

    def get_level_title(self, obj):
        return self._level_info(obj).title

    def get_next_threshold(self, obj):
        return self._level_info(obj).next_threshold

    def get_progress_pct(self, obj):
        return self._level_info(obj).progress_pct


class MeGamificationSerializer(_LevelMixin, serializers.ModelSerializer):
    points = serializers.IntegerField(source="total", read_only=True)
    badges = serializers.SerializerMethodField()
    recent_transactions = serializers.SerializerMethodField()

    class Meta:
        model = UserPointsBalance
        fields = [
            "points",
            "level",
            "level_title",
            "next_threshold",
            "progress_pct",
            "badges",
            "recent_transactions",
        ]

    def get_badges(self, obj):
        qs = (
            UserBadge.objects.filter(user_id=obj.user_id)
            .select_related("badge")
            .order_by("-awarded_at")
        )
        return UserBadgeSerializer(qs, many=True).data

    def get_recent_transactions(self, obj):
        qs = PointsTransaction.objects.filter(user_id=obj.user_id).order_by(
            "-created_at"
        )[:10]
        return PointsTransactionSerializer(qs, many=True).data


class PublicGamificationSerializer(_LevelMixin, serializers.ModelSerializer):
    """Public-facing subset (no transaction log)."""

    user_id = serializers.IntegerField(read_only=True)
    points = serializers.IntegerField(source="total", read_only=True)
    badges = serializers.SerializerMethodField()

    class Meta:
        model = UserPointsBalance
        fields = [
            "user_id",
            "points",
            "level",
            "level_title",
            "next_threshold",
            "progress_pct",
            "badges",
        ]

    def get_badges(self, obj):
        qs = (
            UserBadge.objects.filter(user_id=obj.user_id)
            .select_related("badge")
            .order_by("-awarded_at")
        )
        return UserBadgeSerializer(qs, many=True).data


class LeaderboardEntrySerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    points = serializers.IntegerField()
    level = serializers.IntegerField()
    level_title = serializers.CharField()
