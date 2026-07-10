"""Notification fan-out for review moderation.

Shared by the API moderation endpoint and the Django admin so both paths
produce the same notifications. Callers are responsible for the state
guard (only fan out on a pending → approved transition).
"""

from notifications.services import notify, notify_many
from places.models import PlaceFavorite


def notify_review_moderated(review, action: str, reason: str = "") -> None:
    """Tell the review's author their review was approved or rejected."""
    notify(
        review.author,
        "review_approved" if action == "approve" else "review_rejected",
        review_id=review.id,
        place_id=review.place_id,
        place_name=review.place.name if review.place_id else "",
        reason=reason or "",
    )


def notify_favoriters_of_new_review(review) -> None:
    """Tell everyone who favorited the place about a fresh public review.

    A new public review is the strongest reason for fans of the place to
    come back — everyone who favorited it gets a ping, except the reviewer
    themselves.
    """
    if not review.place_id:
        return
    favoriter_ids = (
        PlaceFavorite.objects.filter(
            place_id=review.place_id,
            user__is_active=True,
            user__is_banned=False,
        )
        .exclude(user_id=review.author_id)
        .values_list("user_id", flat=True)
    )
    notify_many(
        favoriter_ids,
        "favorite_place_review",
        review_id=review.id,
        place_id=review.place_id,
        place_name=review.place.name,
        review_author=review.author.username if review.author_id else "",
    )
