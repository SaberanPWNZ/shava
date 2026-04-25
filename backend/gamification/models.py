"""Domain models for the gamification subsystem.

Designed as a self-contained package so that other apps (notably
``reviews``) remain unaware of it. Integration happens via Django
signals registered in :mod:`gamification.apps`.

Models
------
- :class:`PointsTransaction` — append-only ledger; the source of truth.
- :class:`UserPointsBalance`  — denormalised cache of total points and
  current level for fast reads. Updated transactionally after every
  insert into :class:`PointsTransaction`.
- :class:`Badge`              — catalogue of available achievements.
- :class:`UserBadge`          — many-to-many through model awarding a
  badge to a user.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models

from .rules import REASON_CHOICES


class PointsTransaction(models.Model):
    """Single append-only entry recording a point change."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="points_transactions",
    )
    amount = models.IntegerField(
        help_text="Positive for awards, negative for adjustments/penalties."
    )
    reason = models.CharField(max_length=64, choices=REASON_CHOICES)
    # Generic-style reference to the entity that triggered the award.
    # We avoid Django's GenericForeignKey on purpose to keep the schema
    # simple and make the unique index portable.
    ref_type = models.CharField(max_length=64, blank=True, default="")
    ref_id = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Points transaction"
        verbose_name_plural = "Points transactions"
        ordering = ["-created_at"]
        constraints = [
            # Idempotency guarantee: a given (user, reason, ref) tuple
            # can be inserted at most once. Re-running a signal handler
            # will therefore be a no-op.
            models.UniqueConstraint(
                fields=["user", "reason", "ref_type", "ref_id"],
                name="uniq_points_tx_user_reason_ref",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"{self.user_id}: {self.amount:+d} ({self.reason})"


class UserPointsBalance(models.Model):
    """Denormalised running total + current level for quick reads."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="points_balance",
    )
    total = models.PositiveIntegerField(default=0)
    level = models.PositiveSmallIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User points balance"
        verbose_name_plural = "User points balances"
        ordering = ["-total"]

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"{self.user_id}: {self.total} pts (lvl {self.level})"


class Badge(models.Model):
    """A catalogue entry. Awarded to users via :class:`UserBadge`."""

    TIER_BRONZE = "bronze"
    TIER_SILVER = "silver"
    TIER_GOLD = "gold"
    TIER_CHOICES = [
        (TIER_BRONZE, "Bronze"),
        (TIER_SILVER, "Silver"),
        (TIER_GOLD, "Gold"),
    ]

    code = models.SlugField(max_length=64, unique=True)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")
    icon = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="Front-end icon slug or emoji.",
    )
    points_reward = models.PositiveIntegerField(default=0)
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default=TIER_BRONZE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Badge"
        verbose_name_plural = "Badges"
        ordering = ["tier", "title"]

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"{self.title} ({self.code})"


class UserBadge(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_badges",
    )
    badge = models.ForeignKey(
        Badge, on_delete=models.CASCADE, related_name="awarded_to"
    )
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User badge"
        verbose_name_plural = "User badges"
        ordering = ["-awarded_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "badge"], name="uniq_user_badge"
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"{self.user_id} → {self.badge.code}"
