"""Configurable rules: events that produce points.

Each rule is keyed by a stable ``reason`` code and declares the points
to award. New events are added by extending this dictionary — services
and signal handlers do not need to change. This keeps the design
open/closed (OCP).
"""

from __future__ import annotations

from dataclasses import dataclass

# Reason codes (kept as plain strings — used as DB choices and as keys).
REVIEW_CREATED = "REVIEW_CREATED"
REVIEW_FIRST_FOR_PLACE = "REVIEW_FIRST_FOR_PLACE"
REVIEW_PHOTO = "REVIEW_PHOTO"
REVIEW_VERIFIED = "REVIEW_VERIFIED"
REVIEW_HELPFUL_VOTE = "REVIEW_HELPFUL_VOTE"
BADGE_AWARDED = "BADGE_AWARDED"
MANUAL_ADJUSTMENT = "MANUAL_ADJUSTMENT"


REASON_CHOICES: list[tuple[str, str]] = [
    (REVIEW_CREATED, "Review created"),
    (REVIEW_FIRST_FOR_PLACE, "First review for place"),
    (REVIEW_PHOTO, "Review with dish photo"),
    (REVIEW_VERIFIED, "Review verified by moderator"),
    (REVIEW_HELPFUL_VOTE, "Review marked as helpful"),
    (BADGE_AWARDED, "Badge awarded"),
    (MANUAL_ADJUSTMENT, "Manual adjustment"),
]


@dataclass(frozen=True)
class Rule:
    reason: str
    amount: int
    description: str


# Default point values for each event. Negative amounts are allowed for
# moderation/abuse penalties (handled via :data:`MANUAL_ADJUSTMENT`).
RULES: dict[str, Rule] = {
    REVIEW_CREATED: Rule(REVIEW_CREATED, 10, "Posting a review"),
    REVIEW_FIRST_FOR_PLACE: Rule(
        REVIEW_FIRST_FOR_PLACE, 20, "First review for a place"
    ),
    REVIEW_PHOTO: Rule(REVIEW_PHOTO, 5, "Attaching a dish photo to a review"),
    REVIEW_VERIFIED: Rule(
        REVIEW_VERIFIED, 30, "Review verified by moderator (receipt photo)"
    ),
    REVIEW_HELPFUL_VOTE: Rule(
        REVIEW_HELPFUL_VOTE, 1, "Another user marked your review as helpful"
    ),
}


def points_for(reason: str) -> int:
    rule = RULES.get(reason)
    return rule.amount if rule is not None else 0
