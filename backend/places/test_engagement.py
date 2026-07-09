"""Tests for the engagement endpoints: favorites, viewer context on the
place detail, the public review feed, review-list ordering and the
"edited review goes back to moderation" rule."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from places.models import Place, PlaceFavorite, PlaceRating
from reviews.models import Review

User = get_user_model()


def make_place(author, name="Shava Spot", place_status="Active"):
    return Place.objects.create(
        name=name,
        district="Unknown",
        address="Test Address",
        latitude=50.4501,
        longitude=30.5234,
        main_image="test.jpg",
        status=place_status,
        author=author,
    )


class FavoriteTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="fav@example.com", password="testpass123", username="fav"
        )
        self.other = User.objects.create_user(
            email="other@example.com", password="testpass123", username="other"
        )
        self.place = make_place(self.other)
        self.client.force_authenticate(user=self.user)

    def test_favorite_toggle_is_idempotent(self):
        url = f"/api/places/{self.place.pk}/favorite/"
        first = self.client.post(url)
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(first.data, {"favorites_count": 1, "favorited": True})
        repeat = self.client.post(url)
        self.assertEqual(repeat.status_code, status.HTTP_200_OK)
        self.assertEqual(repeat.data["favorites_count"], 1)
        removed = self.client.delete(url)
        self.assertEqual(removed.status_code, status.HTTP_200_OK)
        self.assertEqual(removed.data, {"favorites_count": 0, "favorited": False})
        # Deleting again stays a calm 200, not an error.
        again = self.client.delete(url)
        self.assertEqual(again.status_code, status.HTTP_200_OK)

    def test_favorite_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(f"/api/places/{self.place.pk}/favorite/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_favorite_hidden_place(self):
        hidden = make_place(self.other, name="Pending", place_status="On_moderation")
        response = self.client.post(f"/api/places/{hidden.pk}/favorite/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_favorites_list_returns_only_mine_newest_first(self):
        second = make_place(self.other, name="Second Spot")
        PlaceFavorite.objects.create(user=self.user, place=self.place)
        PlaceFavorite.objects.create(user=self.user, place=second)
        PlaceFavorite.objects.create(user=self.other, place=self.place)
        response = self.client.get("/api/places/favorites/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [row["name"] for row in response.data["results"]]
        self.assertEqual(names, ["Second Spot", "Shava Spot"])
        # Count aggregates *all* users, viewer flag is personal.
        first_row = next(
            row for row in response.data["results"] if row["name"] == "Shava Spot"
        )
        self.assertEqual(first_row["favorites_count"], 2)
        self.assertTrue(first_row["is_favorited"])

    def test_places_list_carries_is_favorited_flag(self):
        PlaceFavorite.objects.create(user=self.user, place=self.place)
        response = self.client.get("/api/places/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        row = next(r for r in response.data["results"] if r["id"] == self.place.pk)
        self.assertTrue(row["is_favorited"])
        # Anonymous viewers just get False.
        self.client.force_authenticate(user=None)
        anon = self.client.get("/api/places/")
        anon_row = next(r for r in anon.data["results"] if r["id"] == self.place.pk)
        self.assertFalse(anon_row["is_favorited"])


class PlaceViewerContextTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="viewer@example.com", password="testpass123", username="viewer"
        )
        self.place = make_place(self.user)
        self.client.force_authenticate(user=self.user)

    def test_detail_exposes_viewer_rating_and_review(self):
        PlaceRating.objects.create(
            user=self.user, place=self.place, rating=Decimal("8.0")
        )
        review = Review.objects.create(
            place=self.place, author=self.user, score=Decimal("8.0"), comment="ok"
        )
        response = self.client.get(f"/api/places/place/{self.place.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["viewer_rating"], 4.0)
        self.assertEqual(response.data["viewer_review_id"], review.id)

    def test_detail_viewer_fields_default_to_none(self):
        response = self.client.get(f"/api/places/place/{self.place.pk}/")
        self.assertIsNone(response.data["viewer_rating"])
        self.assertIsNone(response.data["viewer_review_id"])
        self.client.force_authenticate(user=None)
        anon = self.client.get(f"/api/places/place/{self.place.pk}/")
        self.assertIsNone(anon.data["viewer_rating"])


class ReviewFeedAndOrderingTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            email="author@example.com", password="testpass123", username="author"
        )
        self.place = make_place(self.author)
        self.approved_low = Review.objects.create(
            place=self.place,
            author=self.author,
            score=Decimal("2.0"),
            comment="meh",
            is_moderated=True,
        )
        self.approved_top = Review.objects.create(
            place=self.place,
            author=self.author,
            score=Decimal("10.0"),
            comment="great",
            is_moderated=True,
            helpful_count=5,
            dish_image="review_dishes/pic.jpg",
        )
        self.pending = Review.objects.create(
            place=self.place, author=self.author, score=Decimal("6.0"), comment="wip"
        )

    def test_feed_lists_only_approved_reviews_publicly(self):
        response = self.client.get("/api/reviews/feed/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [row["id"] for row in response.data["results"]]
        self.assertIn(self.approved_top.id, ids)
        self.assertNotIn(self.pending.id, ids)
        # Newest first.
        self.assertEqual(ids[0], self.approved_top.id)

    def test_feed_filters_by_city(self):
        response = self.client.get("/api/reviews/feed/?city=Львів")
        self.assertEqual(response.data["results"], [])
        match = self.client.get("/api/reviews/feed/?city=Київ")
        self.assertEqual(len(match.data["results"]), 2)

    def test_place_reviews_ordering_and_photo_filter(self):
        base = f"/api/places/{self.place.pk}/reviews/"
        helpful = self.client.get(base + "?ordering=helpful")
        self.assertEqual(helpful.data["results"][0]["id"], self.approved_top.id)
        low = self.client.get(base + "?ordering=low")
        self.assertEqual(low.data["results"][0]["id"], self.approved_low.id)
        photos = self.client.get(base + "?with_photos=1")
        ids = [row["id"] for row in photos.data["results"]]
        self.assertEqual(ids, [self.approved_top.id])


class ReviewEditModerationResetTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            email="editor@example.com", password="testpass123", username="editor"
        )
        self.place = make_place(self.author)
        self.review = Review.objects.create(
            place=self.place,
            author=self.author,
            score=Decimal("10.0"),
            comment="honest review",
            is_moderated=True,
        )
        self.place.recalculate_rating_from_reviews()
        self.client.force_authenticate(user=self.author)

    def test_editing_approved_review_sends_it_back_to_moderation(self):
        response = self.client.patch(
            f"/api/reviews/my-reviews/{self.review.pk}/",
            {"comment": "actually, changed my mind", "score": "2.0"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertFalse(self.review.is_moderated)
        # The place rating no longer counts the now-unapproved review.
        self.place.refresh_from_db()
        self.assertEqual(self.place.rating, Decimal("0.0"))
