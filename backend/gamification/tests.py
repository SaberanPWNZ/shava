"""Tests for the gamification subsystem."""

from __future__ import annotations

from decimal import Decimal

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from gamification.levels import level_for
from gamification.models import (
    Badge,
    PointsTransaction,
    UserBadge,
    UserPointsBalance,
)
from gamification.rules import (
    REVIEW_CREATED,
    REVIEW_FIRST_FOR_PLACE,
    REVIEW_HELPFUL_VOTE,
    REVIEW_VERIFIED,
)
from gamification.services import PointsService
from places.models import Place
from reviews.models import Review, ReviewHelpfulVote
from users.models import User

NO_THROTTLE = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "auth": "1000/min",
        "register": "1000/min",
        "helpful": "1000/min",
    },
}


def _make_place(name="Test Place", **kwargs):
    """Helper to create a Place skipping the required main_image field."""

    return Place.objects.create(
        name=name,
        district=kwargs.get("district", "Unknown"),
        address=kwargs.get("address", "Somewhere 1"),
        main_image=kwargs.get("main_image", "place_images/test.png"),
    )


class LevelHelperTests(TestCase):
    def test_level_for_zero(self):
        info = level_for(0)
        self.assertEqual(info.level, 0)
        self.assertEqual(info.title, "Newbie")
        self.assertEqual(info.next_threshold, 50)
        self.assertEqual(info.progress_pct, 0)

    def test_level_for_mid_tier(self):
        info = level_for(75)
        self.assertEqual(info.level, 1)
        self.assertEqual(info.title, "Foodie")
        self.assertEqual(info.next_threshold, 150)
        self.assertGreater(info.progress_pct, 0)
        self.assertLess(info.progress_pct, 100)

    def test_level_for_max(self):
        info = level_for(10_000)
        self.assertEqual(info.level, 5)
        self.assertEqual(info.title, "Legend")
        self.assertIsNone(info.next_threshold)
        self.assertEqual(info.progress_pct, 100)


class PointsServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="alice@example.com", password="StrongPass!234"
        )

    def test_award_creates_transaction_and_balance(self):
        result = PointsService.award(
            self.user, REVIEW_CREATED, ref_type="review", ref_id=1
        )
        self.assertTrue(result.created)
        self.assertEqual(result.balance.total, 10)
        self.assertEqual(result.balance.level, 0)
        self.assertEqual(PointsTransaction.objects.count(), 1)

    def test_award_is_idempotent(self):
        PointsService.award(self.user, REVIEW_CREATED, ref_type="review", ref_id=42)
        second = PointsService.award(
            self.user, REVIEW_CREATED, ref_type="review", ref_id=42
        )
        self.assertFalse(second.created)
        self.assertEqual(PointsTransaction.objects.count(), 1)
        self.assertEqual(UserPointsBalance.objects.get(user=self.user).total, 10)

    def test_award_updates_level(self):
        # Need 50 points to reach Foodie. 5 distinct refs × 10 pts.
        for i in range(5):
            PointsService.award(
                self.user, REVIEW_CREATED, ref_type="review", ref_id=i + 1
            )
        balance = UserPointsBalance.objects.get(user=self.user)
        self.assertEqual(balance.total, 50)
        self.assertEqual(balance.level, 1)

    def test_negative_adjustment_clamps_at_zero(self):
        PointsService.award(self.user, REVIEW_CREATED, ref_type="r", ref_id=1)
        # Manual penalty of -100 — should clamp at 0.
        PointsService.award(
            self.user,
            "MANUAL_ADJUSTMENT",
            amount=-100,
            ref_type="penalty",
            ref_id=1,
        )
        self.assertEqual(UserPointsBalance.objects.get(user=self.user).total, 0)


class ReviewSignalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="bob@example.com", password="StrongPass!234"
        )
        self.place = _make_place()

    def test_review_creation_awards_points(self):
        Review.objects.create(
            place=self.place,
            author=self.user,
            score=Decimal("8.0"),
            comment="great",
        )
        balance = UserPointsBalance.objects.get(user=self.user)
        # REVIEW_CREATED (10) + REVIEW_FIRST_FOR_PLACE (20) = 30
        self.assertEqual(balance.total, 30)
        reasons = set(
            PointsTransaction.objects.filter(user=self.user).values_list(
                "reason", flat=True
            )
        )
        self.assertIn(REVIEW_CREATED, reasons)
        self.assertIn(REVIEW_FIRST_FOR_PLACE, reasons)

    def test_first_for_place_only_for_first_author(self):
        other = User.objects.create_user(
            email="c@example.com", password="StrongPass!234"
        )
        Review.objects.create(place=self.place, author=self.user, score=Decimal("8.0"))
        Review.objects.create(place=self.place, author=other, score=Decimal("9.0"))
        other_reasons = set(
            PointsTransaction.objects.filter(user=other).values_list(
                "reason", flat=True
            )
        )
        self.assertIn(REVIEW_CREATED, other_reasons)
        self.assertNotIn(REVIEW_FIRST_FOR_PLACE, other_reasons)

    def test_verification_awards_points_only_on_transition(self):
        review = Review.objects.create(
            place=self.place, author=self.user, score=Decimal("8.0")
        )
        before = UserPointsBalance.objects.get(user=self.user).total

        review.is_verified = True
        review.save(update_fields=["is_verified"])

        balance = UserPointsBalance.objects.get(user=self.user)
        self.assertEqual(balance.total, before + 30)
        self.assertEqual(
            PointsTransaction.objects.filter(
                user=self.user, reason=REVIEW_VERIFIED
            ).count(),
            1,
        )

        # Saving again with is_verified already True should not award again.
        review.save(update_fields=["is_verified"])
        self.assertEqual(
            PointsTransaction.objects.filter(
                user=self.user, reason=REVIEW_VERIFIED
            ).count(),
            1,
        )


class BadgeServiceTests(TestCase):
    def setUp(self):
        # Badges must be present (data migration runs in real DB but
        # not during test transaction setup; create explicitly).
        Badge.objects.update_or_create(
            code="first_review",
            defaults={
                "title": "First Review",
                "description": "First!",
                "tier": Badge.TIER_BRONZE,
            },
        )
        self.user = User.objects.create_user(
            email="carol@example.com", password="StrongPass!234"
        )
        self.place = _make_place()

    def test_first_review_badge_awarded_once(self):
        Review.objects.create(place=self.place, author=self.user, score=Decimal("8.0"))
        self.assertTrue(
            UserBadge.objects.filter(
                user=self.user, badge__code="first_review"
            ).exists()
        )
        # Creating a second review should not duplicate the badge.
        other = _make_place(name="Other")
        Review.objects.create(place=other, author=self.user, score=Decimal("9.0"))
        self.assertEqual(
            UserBadge.objects.filter(
                user=self.user, badge__code="first_review"
            ).count(),
            1,
        )


@override_settings(REST_FRAMEWORK={**NO_THROTTLE})
class GamificationApiTests(APITestCase):
    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.user = User.objects.create_user(
            email="d@example.com", password="StrongPass!234"
        )
        self.place = _make_place()

    def _login(self):
        resp = self.client.post(
            "/api/users/login/",
            {"email": "d@example.com", "password": "StrongPass!234"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")

    def test_me_requires_auth(self):
        resp = self.client.get("/api/gamification/me/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_balance_and_level(self):
        self._login()
        resp = self.client.get("/api/gamification/me/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["points"], 0)
        self.assertEqual(resp.data["level"], 0)
        self.assertEqual(resp.data["level_title"], "Newbie")
        self.assertIn("badges", resp.data)
        self.assertIn("recent_transactions", resp.data)

    def test_public_profile_is_open(self):
        resp = self.client.get(f"/api/gamification/users/{self.user.id}/public/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["user_id"], self.user.id)
        self.assertEqual(resp.data["points"], 0)

    def test_badges_catalogue(self):
        Badge.objects.create(
            code="x", title="X", tier=Badge.TIER_BRONZE, is_active=True
        )
        resp = self.client.get("/api/gamification/badges/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        codes = [b["code"] for b in resp.data]
        self.assertIn("x", codes)

    def test_leaderboard_period_validation(self):
        resp = self.client.get("/api/gamification/leaderboard/?period=bogus")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_leaderboard_returns_ranked_users(self):
        Review.objects.create(place=self.place, author=self.user, score=Decimal("8.0"))
        resp = self.client.get("/api/gamification/leaderboard/?period=all")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["period"], "all")
        users_in_board = [r["user_id"] for r in resp.data["results"]]
        self.assertIn(self.user.id, users_in_board)


@override_settings(REST_FRAMEWORK={**NO_THROTTLE})
class HelpfulVoteApiTests(APITestCase):
    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.author = User.objects.create_user(
            email="author@example.com", password="StrongPass!234"
        )
        self.voter = User.objects.create_user(
            email="voter@example.com", password="StrongPass!234"
        )
        self.place = _make_place()
        self.review = Review.objects.create(
            place=self.place, author=self.author, score=Decimal("8.0")
        )

    def _login_as(self, email):
        resp = self.client.post(
            "/api/users/login/",
            {"email": email, "password": "StrongPass!234"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")

    def test_helpful_requires_auth(self):
        resp = self.client.post(f"/api/reviews/{self.review.id}/helpful/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_vote_own_review(self):
        self._login_as("author@example.com")
        resp = self.client.post(f"/api/reviews/{self.review.id}/helpful/")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_helpful_vote_awards_author(self):
        self._login_as("voter@example.com")
        before = PointsTransaction.objects.filter(
            user=self.author, reason=REVIEW_HELPFUL_VOTE
        ).count()
        resp = self.client.post(f"/api/reviews/{self.review.id}/helpful/")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["helpful_count"], 1)
        after = PointsTransaction.objects.filter(
            user=self.author, reason=REVIEW_HELPFUL_VOTE
        ).count()
        self.assertEqual(after, before + 1)

    def test_helpful_vote_is_idempotent(self):
        self._login_as("voter@example.com")
        self.client.post(f"/api/reviews/{self.review.id}/helpful/")
        # Repeat — same user, same review.
        resp = self.client.post(f"/api/reviews/{self.review.id}/helpful/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.helpful_count, 1)
        self.assertEqual(
            ReviewHelpfulVote.objects.filter(
                review=self.review, user=self.voter
            ).count(),
            1,
        )

    def test_helpful_unvote(self):
        self._login_as("voter@example.com")
        self.client.post(f"/api/reviews/{self.review.id}/helpful/")
        resp = self.client.delete(f"/api/reviews/{self.review.id}/helpful/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.helpful_count, 0)
