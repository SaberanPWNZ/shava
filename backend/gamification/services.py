"""Application services for the gamification domain.

Following SRP: views and signal handlers stay thin and delegate the
actual business logic to these services. They are also the only place
that should mutate :class:`UserPointsBalance` and create
:class:`PointsTransaction` rows.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from django.db import IntegrityError, transaction

from notifications.services import notify

from .levels import level_for
from .models import Badge, PointsTransaction, UserBadge, UserPointsBalance
from .rules import points_for

logger = logging.getLogger("gamification")


@dataclass(frozen=True)
class AwardResult:
    """Outcome of an :meth:`PointsService.award` call."""

    transaction: PointsTransaction | None
    balance: UserPointsBalance
    awarded_badges: list[Badge]
    leveled_up: bool
    created: bool  # ``False`` when the call was a no-op (idempotent hit).


class PointsService:
    """Pure service object for awarding points.

    Why a service:
      * The signal handler should not know about ``select_for_update``
        or how the cache is updated.
      * Tests can call :meth:`award` directly without firing signals.
      * It is the single place where the idempotency invariant is
        enforced.
    """

    @staticmethod
    @transaction.atomic
    def award(
        user,
        reason: str,
        *,
        amount: int | None = None,
        ref_type: str = "",
        ref_id: int = 0,
        check_badges: bool = True,
    ) -> AwardResult:
        """Award (or adjust) points for ``user``.

        Idempotent across retries: ``(user, reason, ref_type, ref_id)``
        is unique. Re-calling with the same arguments returns an
        :class:`AwardResult` with ``created=False`` and no balance
        delta.
        """

        if amount is None:
            amount = points_for(reason)

        # Lock (or create) the balance row first so concurrent awards
        # for the same user serialise cleanly.
        balance, _ = UserPointsBalance.objects.select_for_update().get_or_create(
            user=user
        )

        try:
            with transaction.atomic():
                tx = PointsTransaction.objects.create(
                    user=user,
                    amount=int(amount),
                    reason=reason,
                    ref_type=ref_type or "",
                    ref_id=int(ref_id or 0),
                )
        except IntegrityError:
            # The unique constraint kicked in — same logical event was
            # already awarded. Treat as a successful no-op.
            logger.debug(
                "PointsService.award: idempotent hit user=%s reason=%s ref=%s/%s",
                getattr(user, "id", None),
                reason,
                ref_type,
                ref_id,
            )
            return AwardResult(
                transaction=None,
                balance=balance,
                awarded_badges=[],
                leveled_up=False,
                created=False,
            )

        # Apply the delta. ``total`` is a PositiveIntegerField; clamp at
        # zero in case of a negative adjustment that would underflow.
        new_total = max(0, int(balance.total) + int(amount))
        old_level = balance.level
        new_level = level_for(new_total).level
        balance.total = new_total
        balance.level = new_level
        balance.save(update_fields=["total", "level", "updated_at"])

        leveled_up = new_level > old_level

        awarded_badges: list[Badge] = []
        if check_badges:
            awarded_badges = BadgeService.evaluate(user, trigger=reason)

        return AwardResult(
            transaction=tx,
            balance=balance,
            awarded_badges=awarded_badges,
            leveled_up=leveled_up,
            created=True,
        )


# ---------------------------------------------------------------------------
# Badges
# ---------------------------------------------------------------------------


class BadgeService:
    """Evaluates the declarative catalogue in :mod:`gamification.badges`.

    Badges are grouped by metric: each metric function runs at most once
    per evaluation pass, and only when at least one of its badges is
    still unearned — so a 60-badge catalogue stays a handful of queries
    for an active user.
    """

    @staticmethod
    def evaluate(user, *, trigger: str | None = None) -> list[Badge]:
        """Return the list of newly-awarded badges (may be empty)."""

        from .badges import BADGES, METRICS

        # Pre-fetch existing memberships and the catalogue once.
        already = set(
            UserBadge.objects.filter(user=user).values_list("badge__code", flat=True)
        )
        catalogue = {b.code: b for b in Badge.objects.filter(is_active=True)}

        metric_cache: dict[str, int] = {}
        new_badges: list[Badge] = []
        for definition in BADGES:
            if definition.code in already:
                continue
            badge = catalogue.get(definition.code)
            if badge is None:
                # Catalogue not seeded for this code — skip silently so
                # tests and partial deployments do not crash.
                continue
            if definition.metric not in metric_cache:
                metric_fn = METRICS.get(definition.metric)
                if metric_fn is None:
                    continue
                metric_cache[definition.metric] = int(metric_fn(user) or 0)
            if metric_cache[definition.metric] < definition.threshold:
                continue
            try:
                UserBadge.objects.create(user=user, badge=badge)
            except IntegrityError:
                # Race: another request awarded the same badge.
                continue
            new_badges.append(badge)
            notify(
                user,
                "badge_awarded",
                badge_code=badge.code,
                badge_title=badge.title,
                badge_icon=badge.icon,
            )
            if badge.points_reward:
                PointsService.award(
                    user,
                    reason="BADGE_AWARDED",
                    amount=badge.points_reward,
                    ref_type="badge",
                    ref_id=badge.id,
                    check_badges=False,
                )
        return new_badges
