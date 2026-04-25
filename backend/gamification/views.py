"""HTTP API for the gamification subsystem.

Views are intentionally thin — heavy lifting is in
:mod:`gamification.services` and :mod:`gamification.serializers`.
"""

from __future__ import annotations

import logging
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status, views
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .levels import level_for
from .models import Badge, PointsTransaction, UserPointsBalance
from .serializers import (
    BadgeSerializer,
    LeaderboardEntrySerializer,
    MeGamificationSerializer,
    PublicGamificationSerializer,
)

logger = logging.getLogger("gamification")
User = get_user_model()


class MeGamificationView(views.APIView):
    """`GET /api/gamification/me/` — current user's points/level/badges."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        balance, _ = UserPointsBalance.objects.get_or_create(user=request.user)
        return Response(MeGamificationSerializer(balance).data)


class PublicUserGamificationView(views.APIView):
    """`GET /api/gamification/users/<id>/public/`."""

    permission_classes = [AllowAny]

    def get(self, request, pk: int):
        user = get_object_or_404(User, pk=pk)
        balance, _ = UserPointsBalance.objects.get_or_create(user=user)
        data = PublicGamificationSerializer(balance).data
        data["user_id"] = user.id
        data["username"] = user.username
        return Response(data)


class BadgeCatalogueView(generics.ListAPIView):
    """`GET /api/gamification/badges/` — full catalogue (public)."""

    permission_classes = [AllowAny]
    serializer_class = BadgeSerializer
    pagination_class = None

    def get_queryset(self):
        return Badge.objects.filter(is_active=True).order_by("tier", "title")


class LeaderboardView(views.APIView):
    """`GET /api/gamification/leaderboard/?period=week|month|all`."""

    permission_classes = [AllowAny]
    PERIODS = {"week": 7, "month": 30, "all": None}

    def get(self, request):
        period = request.query_params.get("period", "all")
        if period not in self.PERIODS:
            return Response(
                {"detail": "Unknown period. Use one of: week, month, all."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        days = self.PERIODS[period]

        qs = PointsTransaction.objects.all()
        if days is not None:
            since = timezone.now() - timedelta(days=days)
            qs = qs.filter(created_at__gte=since)

        rows = (
            qs.values("user_id", "user__username")
            .annotate(points=Sum("amount"))
            .order_by("-points")[:50]
        )

        entries = []
        for row in rows:
            pts = max(0, int(row["points"] or 0))
            info = level_for(pts)
            entries.append(
                {
                    "user_id": row["user_id"],
                    "username": row["user__username"] or "",
                    "points": pts,
                    "level": info.level,
                    "level_title": info.title,
                }
            )

        return Response(
            {
                "period": period,
                "results": LeaderboardEntrySerializer(entries, many=True).data,
            }
        )


class ReviewHelpfulView(views.APIView):
    """POST/DELETE `/api/reviews/<id>/helpful/` — toggle a helpful vote."""

    permission_classes = [IsAuthenticated]
    throttle_scope = "helpful"

    def post(self, request, pk: int):
        from django.db import transaction
        from django.db.models import F

        from reviews.models import Review, ReviewHelpfulVote

        review = get_object_or_404(Review, pk=pk, is_deleted=False)
        if review.author_id == request.user.id:
            return Response(
                {"detail": "You can't vote on your own review."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            _, created = ReviewHelpfulVote.objects.get_or_create(
                review=review, user=request.user
            )
            if created:
                Review.objects.filter(pk=review.pk).update(
                    helpful_count=F("helpful_count") + 1
                )
        review.refresh_from_db(fields=["helpful_count"])
        return Response(
            {"helpful_count": review.helpful_count, "voted": True},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def delete(self, request, pk: int):
        from django.db import transaction
        from django.db.models import F

        from reviews.models import Review, ReviewHelpfulVote

        review = get_object_or_404(Review, pk=pk, is_deleted=False)
        with transaction.atomic():
            deleted, _ = ReviewHelpfulVote.objects.filter(
                review=review, user=request.user
            ).delete()
            if deleted:
                Review.objects.filter(pk=review.pk).update(
                    helpful_count=F("helpful_count") - 1
                )
        review.refresh_from_db(fields=["helpful_count"])
        return Response({"helpful_count": review.helpful_count, "voted": False})
