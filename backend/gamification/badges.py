"""Declarative badge catalogue.

Every badge is a :class:`BadgeDef`: a metric name plus a threshold. The
metric functions below turn a user into a single integer, and
:meth:`gamification.services.BadgeService.evaluate` computes each metric
at most once per evaluation pass — so adding badges to an existing
metric family costs nothing extra at runtime.

Adding a badge:
1. add a :class:`BadgeDef` to :data:`BADGES` (new metric functions go in
   :data:`METRICS`);
2. add the same code to the seed migration (or create the ``Badge`` row
   in the admin) — the evaluator skips codes missing from the DB.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


def _reviews(user) -> int:
    from reviews.models import Review

    return Review.objects.filter(author=user, is_deleted=False).count()


def _verified_reviews(user) -> int:
    from reviews.models import Review

    return Review.objects.filter(
        author=user, is_verified=True, is_deleted=False
    ).count()


def _helpful_received(user) -> int:
    from django.db.models import Sum

    from reviews.models import Review

    agg = Review.objects.filter(author=user, is_deleted=False).aggregate(
        total=Sum("helpful_count")
    )
    return int(agg["total"] or 0)


def _helpful_given(user) -> int:
    from reviews.models import ReviewHelpfulVote

    return ReviewHelpfulVote.objects.filter(user=user).count()


def _replies_written(user) -> int:
    from reviews.models import ReviewReply

    return ReviewReply.objects.filter(author=user, is_deleted=False).count()


def _replies_received(user) -> int:
    from reviews.models import ReviewReply

    return (
        ReviewReply.objects.filter(review__author=user, is_deleted=False)
        .exclude(author=user)
        .count()
    )


def _favorites_given(user) -> int:
    from places.models import PlaceFavorite

    return PlaceFavorite.objects.filter(user=user).count()


def _favorites_received(user) -> int:
    from places.models import PlaceFavorite

    return PlaceFavorite.objects.filter(place__author=user).exclude(user=user).count()


def _places_added(user) -> int:
    from places.models import Place

    return Place.objects.filter(author=user, status="Active").count()


def _first_reviews(user) -> int:
    # "Was the first to review a place" is already recorded as an
    # idempotent points transaction — count those instead of re-deriving
    # the ordering from scratch.
    from gamification.models import PointsTransaction
    from gamification.rules import REVIEW_FIRST_FOR_PLACE

    return PointsTransaction.objects.filter(
        user=user, reason=REVIEW_FIRST_FOR_PLACE
    ).count()


def _photo_reviews(user) -> int:
    from reviews.models import Review

    return (
        Review.objects.filter(author=user, is_deleted=False)
        .exclude(dish_image="")
        .exclude(dish_image__isnull=True)
        .count()
    )


def _ratings_given(user) -> int:
    from places.models import PlaceRating

    return PlaceRating.objects.filter(user=user).count()


def _distinct_places(user) -> int:
    from reviews.models import Review

    return (
        Review.objects.filter(author=user, is_deleted=False)
        .values("place")
        .distinct()
        .count()
    )


def _distinct_districts(user) -> int:
    from reviews.models import Review

    return (
        Review.objects.filter(author=user, is_deleted=False)
        .values("place__district")
        .distinct()
        .count()
    )


def _distinct_cities(user) -> int:
    from reviews.models import Review

    return (
        Review.objects.filter(author=user, is_deleted=False)
        .values("place__city")
        .distinct()
        .count()
    )


def _level(user) -> int:
    from gamification.models import UserPointsBalance

    balance = UserPointsBalance.objects.filter(user=user).only("level").first()
    return balance.level if balance else 0


def _perfect_scores(user) -> int:
    from reviews.models import Review

    return Review.objects.filter(author=user, is_deleted=False, score__gte=10).count()


def _low_scores(user) -> int:
    from reviews.models import Review

    return Review.objects.filter(author=user, is_deleted=False, score__lte=2).count()


def _night_reviews(user) -> int:
    from reviews.models import Review

    return Review.objects.filter(
        author=user, is_deleted=False, created_at__hour__lt=6
    ).count()


def _weekend_reviews(user) -> int:
    from reviews.models import Review

    # Django's week_day lookup: 1 = Sunday, 7 = Saturday.
    return Review.objects.filter(
        author=user, is_deleted=False, created_at__week_day__in=[1, 7]
    ).count()


def _long_reviews(user) -> int:
    from django.db.models.functions import Length

    from reviews.models import Review

    return (
        Review.objects.filter(author=user, is_deleted=False)
        .annotate(comment_len=Length("comment"))
        .filter(comment_len__gte=500)
        .count()
    )


def _active_days(user) -> int:
    from reviews.models import Review

    return (
        Review.objects.filter(author=user, is_deleted=False)
        .values("created_at__date")
        .distinct()
        .count()
    )


def _account_age_days(user) -> int:
    from django.utils import timezone

    joined = getattr(user, "date_joined", None)
    if joined is None:
        return 0
    return (timezone.now() - joined).days


def _badges_earned(user) -> int:
    from gamification.models import UserBadge

    return UserBadge.objects.filter(user=user).count()


METRICS: dict[str, Callable] = {
    "reviews": _reviews,
    "verified_reviews": _verified_reviews,
    "helpful_received": _helpful_received,
    "helpful_given": _helpful_given,
    "replies_written": _replies_written,
    "replies_received": _replies_received,
    "favorites_given": _favorites_given,
    "favorites_received": _favorites_received,
    "places_added": _places_added,
    "first_reviews": _first_reviews,
    "photo_reviews": _photo_reviews,
    "ratings_given": _ratings_given,
    "distinct_places": _distinct_places,
    "distinct_districts": _distinct_districts,
    "distinct_cities": _distinct_cities,
    "level": _level,
    "perfect_scores": _perfect_scores,
    "low_scores": _low_scores,
    "night_reviews": _night_reviews,
    "weekend_reviews": _weekend_reviews,
    "long_reviews": _long_reviews,
    "active_days": _active_days,
    "account_age_days": _account_age_days,
    "badges_earned": _badges_earned,
}


@dataclass(frozen=True)
class BadgeDef:
    code: str
    title: str
    description: str
    icon: str
    tier: str
    points_reward: int
    metric: str
    threshold: int


# One badge per line keeps the catalogue scannable as a table.
# fmt: off
BADGES: list[BadgeDef] = [
    # --- Reviews written -------------------------------------------------
    BadgeDef("first_review", "First Review", "Posted your very first review.", "🥇", "bronze", 0, "reviews", 1),
    BadgeDef("five_reviews", "Warming Up", "Posted five reviews.", "✍️", "bronze", 10, "reviews", 5),
    BadgeDef("ten_reviews", "Ten Reviews", "Posted ten reviews. You're a regular!", "📝", "silver", 25, "reviews", 10),
    BadgeDef("reviews_25", "Storyteller", "Posted 25 reviews.", "📚", "silver", 50, "reviews", 25),
    BadgeDef("reviews_50", "Chronicler", "Posted 50 reviews.", "🖋️", "gold", 100, "reviews", 50),
    BadgeDef("reviews_100", "Century Club", "Posted 100 reviews.", "🏆", "gold", 200, "reviews", 100),
    BadgeDef("reviews_250", "Living Archive", "Posted 250 reviews.", "👑", "platinum", 500, "reviews", 250),
    # --- Verified reviews -------------------------------------------------
    BadgeDef("verified_first", "Receipt Attached", "Your first review verified by moderators.", "🧾", "bronze", 10, "verified_reviews", 1),
    BadgeDef("verified_five", "Verified Five", "Five of your reviews were verified by moderators.", "✅", "silver", 50, "verified_reviews", 5),
    BadgeDef("verified_15", "Trusted Source", "15 verified reviews.", "🔏", "gold", 100, "verified_reviews", 15),
    BadgeDef("verified_50", "Bulletproof", "50 verified reviews.", "🛡️", "platinum", 250, "verified_reviews", 50),
    # --- Helpful votes received -------------------------------------------
    BadgeDef("helpful_10", "Good Advice", "Your reviews were marked helpful 10 times.", "👍", "bronze", 10, "helpful_received", 10),
    BadgeDef("helpful_fifty", "Helpful 50", "Other users marked your reviews as helpful 50 times.", "🤝", "silver", 100, "helpful_received", 50),
    BadgeDef("helpful_100", "Crowd Favorite", "100 helpful votes on your reviews.", "🙌", "gold", 100, "helpful_received", 100),
    BadgeDef("helpful_250", "Voice of Reason", "250 helpful votes on your reviews.", "📣", "gold", 200, "helpful_received", 250),
    BadgeDef("helpful_500", "Community Pillar", "500 helpful votes on your reviews.", "🏛️", "platinum", 500, "helpful_received", 500),
    # --- Helpful votes given ----------------------------------------------
    BadgeDef("voted_10", "Supporter", "Marked 10 reviews as helpful.", "🗳️", "bronze", 5, "helpful_given", 10),
    BadgeDef("voted_50", "Cheerleader", "Marked 50 reviews as helpful.", "📢", "silver", 25, "helpful_given", 50),
    BadgeDef("voted_100", "Talent Scout", "Marked 100 reviews as helpful.", "🔭", "gold", 50, "helpful_given", 100),
    # --- Replies written ---------------------------------------------------
    BadgeDef("first_reply", "Ice Breaker", "Wrote your first reply.", "💬", "bronze", 5, "replies_written", 1),
    BadgeDef("replies_10", "Chatterbox", "Wrote 10 replies.", "🗣️", "bronze", 15, "replies_written", 10),
    BadgeDef("replies_50", "Debater", "Wrote 50 replies.", "🎙️", "silver", 50, "replies_written", 50),
    BadgeDef("replies_100", "Forum Regular", "Wrote 100 replies.", "🪑", "gold", 100, "replies_written", 100),
    # --- Replies received ---------------------------------------------------
    BadgeDef("sparked_10", "Conversation Starter", "Your reviews got 10 replies from others.", "🔥", "silver", 25, "replies_received", 10),
    BadgeDef("sparked_50", "Hot Topic", "Your reviews got 50 replies from others.", "🌋", "gold", 100, "replies_received", 50),
    # --- Favorites given ----------------------------------------------------
    BadgeDef("collector_5", "Wishlist", "Saved 5 places to favorites.", "⭐", "bronze", 5, "favorites_given", 5),
    BadgeDef("collector_25", "Curator", "Saved 25 places to favorites.", "🌟", "silver", 25, "favorites_given", 25),
    # --- Favorites received (on places you added) ---------------------------
    BadgeDef("fan_favorite_10", "Fan Favorite", "Places you added were favorited 10 times.", "💛", "silver", 50, "favorites_received", 10),
    BadgeDef("fan_favorite_50", "Local Legend", "Places you added were favorited 50 times.", "💖", "gold", 150, "favorites_received", 50),
    # --- Places added --------------------------------------------------------
    BadgeDef("place_scout", "Scout", "Added your first approved place.", "📍", "bronze", 20, "places_added", 1),
    BadgeDef("place_scout_5", "Cartographer", "Added 5 approved places.", "🗺️", "silver", 50, "places_added", 5),
    BadgeDef("place_scout_15", "Pathfinder", "Added 15 approved places.", "🧭", "gold", 150, "places_added", 15),
    BadgeDef("place_scout_50", "City Mapper", "Added 50 approved places.", "🛰️", "platinum", 400, "places_added", 50),
    # --- First to review a place ---------------------------------------------
    BadgeDef("pioneer", "Pioneer", "First to review a place.", "🚩", "bronze", 10, "first_reviews", 1),
    BadgeDef("pioneer_5", "Trailblazer", "First to review 5 places.", "⛳", "silver", 50, "first_reviews", 5),
    BadgeDef("pioneer_25", "Frontier Spirit", "First to review 25 places.", "🏔️", "gold", 200, "first_reviews", 25),
    # --- Photo reviews ---------------------------------------------------------
    BadgeDef("first_photo", "Say Cheese", "Attached a photo to a review.", "📸", "bronze", 5, "photo_reviews", 1),
    BadgeDef("photos_10", "Food Photographer", "10 reviews with photos.", "🖼️", "silver", 25, "photo_reviews", 10),
    BadgeDef("photos_50", "Shava Paparazzi", "50 reviews with photos.", "🎞️", "gold", 100, "photo_reviews", 50),
    # --- Ratings given -----------------------------------------------------------
    BadgeDef("rater_10", "Sharp Eye", "Rated 10 places.", "🎯", "bronze", 10, "ratings_given", 10),
    BadgeDef("rater_50", "Scorekeeper", "Rated 50 places.", "🏹", "silver", 50, "ratings_given", 50),
    # --- Exploration ---------------------------------------------------------------
    BadgeDef("explorer_10", "Explorer", "Reviewed 10 different places.", "🧳", "silver", 25, "distinct_places", 10),
    BadgeDef("explorer_30", "Globetrotter", "Reviewed 30 different places.", "🌍", "gold", 100, "distinct_places", 30),
    BadgeDef("districts_5", "District Hopper", "Reviewed places in 5 districts.", "🏙️", "silver", 25, "distinct_districts", 5),
    BadgeDef("districts_10", "Urban Nomad", "Reviewed places in 10 districts.", "🌆", "gold", 75, "distinct_districts", 10),
    BadgeDef("traveler_3", "Traveler", "Reviewed places in 3 cities.", "🚄", "silver", 50, "distinct_cities", 3),
    BadgeDef("traveler_5", "Jetsetter", "Reviewed places in 5 cities.", "✈️", "gold", 100, "distinct_cities", 5),
    # --- Levels -----------------------------------------------------------------------
    BadgeDef("foodie", "Foodie", "Reached the Foodie level (50 points).", "🍽️", "bronze", 0, "level", 1),
    BadgeDef("level_critic", "Critic", "Reached the Critic level (150 points).", "🎓", "silver", 0, "level", 2),
    BadgeDef("level_expert", "Expert", "Reached the Expert level (400 points).", "🥋", "gold", 0, "level", 3),
    BadgeDef("level_master", "Master", "Reached the Master level (1000 points).", "🏅", "gold", 0, "level", 4),
    BadgeDef("level_legend", "Legend", "Reached the Legend level (2500 points).", "🐐", "platinum", 0, "level", 5),
    # --- Personality / fun --------------------------------------------------------------
    BadgeDef("perfect_ten", "Perfect Ten", "Gave a place a flawless 10.", "💯", "bronze", 5, "perfect_scores", 1),
    BadgeDef("tough_critic", "Tough Critic", "Gave a score of 2 or lower. Ouch.", "🌶️", "bronze", 5, "low_scores", 1),
    BadgeDef("night_owl", "Night Owl", "Posted a review between midnight and 6 AM.", "🦉", "bronze", 5, "night_reviews", 1),
    BadgeDef("weekend_warrior", "Weekend Warrior", "Posted 5 reviews on weekends.", "🍻", "bronze", 10, "weekend_reviews", 5),
    BadgeDef("long_read", "Long Read", "Wrote a review of 500+ characters.", "📖", "bronze", 10, "long_reviews", 1),
    # --- Consistency -------------------------------------------------------------------------
    BadgeDef("active_7", "Regular Guest", "Posted reviews on 7 different days.", "📅", "silver", 25, "active_days", 7),
    BadgeDef("active_30", "Part of the Furniture", "Posted reviews on 30 different days.", "🗓️", "gold", 150, "active_days", 30),
    BadgeDef("veteran_year", "One Year With Us", "A member for a full year.", "🎂", "silver", 50, "account_age_days", 365),
    # --- Meta ------------------------------------------------------------------------------------
    BadgeDef("badge_collector_10", "Badge Collector", "Earned 10 badges.", "🎖️", "silver", 25, "badges_earned", 10),
    BadgeDef("badge_collector_25", "Trophy Room", "Earned 25 badges.", "🏵️", "gold", 100, "badges_earned", 25),
]
# fmt: on
