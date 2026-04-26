"""Application services for the gamification domain.

Following SRP: views and signal handlers stay thin and delegate the
actual business logic to these services. They are also the only place
that should mutate :class:`UserPointsBalance` and create
:class:`PointsTransaction` rows.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable

from django.db import IntegrityError, transaction

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


class BadgeStrategy:
    """Predicate that decides whether a badge should be awarded.

    Concrete strategies override :meth:`is_satisfied`. Adding a new
    badge means adding a strategy class and registering its code in
    :data:`BADGE_STRATEGIES` — no other code needs to change (OCP).
    """

    code: str = ""

    def is_satisfied(self, user) -> bool:  # pragma: no cover - abstract
        raise NotImplementedError


class FirstReviewBadge(BadgeStrategy):
    code = "first_review"

    def is_satisfied(self, user) -> bool:
        from reviews.models import Review

        return Review.objects.filter(author=user, is_deleted=False).exists()


class TenReviewsBadge(BadgeStrategy):
    code = "ten_reviews"

    def is_satisfied(self, user) -> bool:
        from reviews.models import Review

        return Review.objects.filter(author=user, is_deleted=False).count() >= 10


class FoodieLevelBadge(BadgeStrategy):
    """Awarded when the user reaches the second level (``Foodie``)."""

    code = "foodie"

    def is_satisfied(self, user) -> bool:
        balance = UserPointsBalance.objects.filter(user=user).only("level").first()
        return bool(balance and balance.level >= 1)


class VerifiedFiveBadge(BadgeStrategy):
    code = "verified_five"

    def is_satisfied(self, user) -> bool:
        from reviews.models import Review

        return (
            Review.objects.filter(
                author=user, is_verified=True, is_deleted=False
            ).count()
            >= 5
        )


class HelpfulFiftyBadge(BadgeStrategy):
    code = "helpful_fifty"

    def is_satisfied(self, user) -> bool:
        from django.db.models import Sum

        from reviews.models import Review

        agg = Review.objects.filter(author=user, is_deleted=False).aggregate(
            total=Sum("helpful_count")
        )
        return int(agg["total"] or 0) >= 50


BADGE_STRATEGIES: list[BadgeStrategy] = [
    FirstReviewBadge(),
    TenReviewsBadge(),
    FoodieLevelBadge(),
    VerifiedFiveBadge(),
    HelpfulFiftyBadge(),
]


class BadgeService:
    """Evaluates badge predicates and awards new badges atomically."""

    @staticmethod
    def evaluate(user, *, trigger: str | None = None) -> list[Badge]:
        """Return the list of newly-awarded badges (may be empty)."""

        # Pre-fetch existing memberships and the catalogue once.
        already = set(
            UserBadge.objects.filter(user=user).values_list("badge__code", flat=True)
        )
        catalogue = {b.code: b for b in Badge.objects.filter(is_active=True)}

        new_badges: list[Badge] = []
        for strategy in BadgeService._strategies_for(trigger):
            if strategy.code in already:
                continue
            badge = catalogue.get(strategy.code)
            if badge is None:
                # Catalogue not seeded for this code — skip silently so
                # tests and partial deployments do not crash.
                continue
            if strategy.is_satisfied(user):
                try:
                    UserBadge.objects.create(user=user, badge=badge)
                except IntegrityError:
                    # Race: another request awarded the same badge.
                    continue
                new_badges.append(badge)
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

    @staticmethod
    def _strategies_for(trigger: str | None) -> Iterable[BadgeStrategy]:
        # In MVP we always evaluate all strategies — they are cheap.
        # Hook left in place so future triggers can narrow the scope.
        return BADGE_STRATEGIES
