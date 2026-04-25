"""Signal handlers — the only place where ``gamification`` reaches into
other apps. Imported (and connected) from :mod:`gamification.apps.ready`.

Disabling the ``gamification`` app removes all of these listeners and
the rest of the system keeps working unchanged (DIP).
"""

from __future__ import annotations

import logging

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver

from . import rules
from .services import PointsService

logger = logging.getLogger("gamification")


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------


def _award_for_new_review(review) -> None:
    """Common logic for a freshly created review."""

    author = getattr(review, "author", None)
    if author is None:
        return

    PointsService.award(
        author,
        reason=rules.REVIEW_CREATED,
        ref_type="review",
        ref_id=review.id,
    )

    # Photo of the dish — small bonus to encourage richer content.
    if getattr(review, "dish_image", None):
        PointsService.award(
            author,
            reason=rules.REVIEW_PHOTO,
            ref_type="review",
            ref_id=review.id,
        )

    # First review for this place across the whole platform.
    place_id = getattr(review, "place_id", None)
    if place_id is not None:
        from reviews.models import Review as _Review

        is_first = (
            _Review.objects.filter(place_id=place_id, is_deleted=False)
            .exclude(pk=review.pk)
            .count()
            == 0
        )
        if is_first:
            PointsService.award(
                author,
                reason=rules.REVIEW_FIRST_FOR_PLACE,
                ref_type="review",
                ref_id=review.id,
            )


def _on_review_post_save(sender, instance, created, **kwargs):
    if created:
        _award_for_new_review(instance)
        return

    # Existing review updated — was ``is_verified`` flipped on?
    flagged_now = getattr(instance, "_was_just_verified", False)
    if flagged_now and getattr(instance, "is_verified", False):
        author = getattr(instance, "author", None)
        if author is not None:
            PointsService.award(
                author,
                reason=rules.REVIEW_VERIFIED,
                ref_type="review",
                ref_id=instance.id,
            )


def _on_review_pre_save(sender, instance, **kwargs):
    """Detect a False→True transition on ``is_verified``.

    Storing a transient flag on the instance avoids needing a separate
    DB lookup in the post_save handler.
    """

    if instance.pk is None:
        instance._was_just_verified = False
        return
    try:
        previous = sender.objects.only("is_verified").get(pk=instance.pk)
    except sender.DoesNotExist:
        instance._was_just_verified = False
        return
    instance._was_just_verified = (
        bool(getattr(instance, "is_verified", False))
        and not bool(previous.is_verified)
    )


# ---------------------------------------------------------------------------
# Helpful votes
# ---------------------------------------------------------------------------


def _on_helpful_vote_created(sender, instance, created, **kwargs):
    if not created:
        return
    review = instance.review
    author = getattr(review, "author", None)
    voter = instance.user
    # Don't reward self-likes.
    if author is None or author == voter or author.id == voter.id:
        return
    PointsService.award(
        author,
        reason=rules.REVIEW_HELPFUL_VOTE,
        ref_type="helpful_vote",
        ref_id=instance.id,
    )


# ---------------------------------------------------------------------------
# Connect signals (called from AppConfig.ready)
# ---------------------------------------------------------------------------


def _connect():
    from reviews.models import Review, ReviewHelpfulVote

    pre_save.connect(_on_review_pre_save, sender=Review, dispatch_uid="gam_review_pre")
    post_save.connect(
        _on_review_post_save, sender=Review, dispatch_uid="gam_review_post"
    )
    post_save.connect(
        _on_helpful_vote_created,
        sender=ReviewHelpfulVote,
        dispatch_uid="gam_helpful_post",
    )


_connect()
