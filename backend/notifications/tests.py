"""Tests for in-app notifications: endpoints and the moderation/reply
triggers wired into the reviews and places apps."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from notifications.models import Notification
from places.models import Place, PlaceFavorite
from reviews.models import Review

User = get_user_model()


def make_place(author, name="Notify Spot", place_status="Active"):
    return Place.objects.create(
        name=name,
        district="Unknown",
        address="Test Address",
        main_image="test.jpg",
        status=place_status,
        author=author,
    )


class NotificationEndpointTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="notify@example.com", password="testpass123", username="notify"
        )
        self.other = User.objects.create_user(
            email="other-n@example.com", password="testpass123", username="othern"
        )
        self.client.force_authenticate(user=self.user)

    def _make(self, user=None, **kwargs):
        return Notification.objects.create(
            user=user or self.user, type="review_approved", data={}, **kwargs
        )

    def test_list_returns_only_mine(self):
        mine = self._make()
        self._make(user=self.other)
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [row["id"] for row in response.data["results"]]
        self.assertEqual(ids, [mine.id])

    def test_unread_count(self):
        self._make()
        self._make(is_read=True)
        response = self.client.get("/api/notifications/unread-count/")
        self.assertEqual(response.data, {"unread": 1})

    def test_mark_read_all_and_by_ids(self):
        first = self._make()
        second = self._make()
        response = self.client.post(
            "/api/notifications/mark-read/", {"ids": [first.id]}, format="json"
        )
        self.assertEqual(response.data, {"marked": 1})
        first.refresh_from_db()
        second.refresh_from_db()
        self.assertTrue(first.is_read)
        self.assertFalse(second.is_read)
        response = self.client.post("/api/notifications/mark-read/", {}, format="json")
        self.assertEqual(response.data, {"marked": 1})

    def test_mark_read_rejects_garbage_ids(self):
        response = self.client.post(
            "/api/notifications/mark-read/", {"ids": ["x"]}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class NotificationTriggerTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            email="author-n@example.com", password="testpass123", username="authorn"
        )
        self.admin = User.objects.create_superuser(
            email="admin-n@example.com", password="testpass123", username="adminn"
        )
        self.place = make_place(self.author)
        self.review = Review.objects.create(
            place=self.place, author=self.author, score=Decimal("8.0"), comment="ok"
        )

    def test_review_moderation_notifies_author(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"/api/reviews/{self.review.pk}/approve/", {}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        note = Notification.objects.get(user=self.author)
        self.assertEqual(note.type, "review_approved")
        self.assertEqual(note.data["place_name"], self.place.name)

    def test_place_moderation_notifies_author(self):
        pending = make_place(self.author, name="Pending", place_status="On_moderation")
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"/api/places/{pending.pk}/reject/", {"reason": "dup"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        note = Notification.objects.get(user=self.author, type="place_rejected")
        self.assertEqual(note.data["reason"], "dup")

    def test_reply_notifies_review_author_but_not_self_reply(self):
        self.review.is_moderated = True
        self.review.save(update_fields=["is_moderated"])
        # Self-reply: no notification.
        self.client.force_authenticate(user=self.author)
        self.client.post(f"/api/reviews/{self.review.pk}/replies/", {"text": "thanks!"})
        self.assertFalse(
            Notification.objects.filter(user=self.author, type="review_reply").exists()
        )
        # Reply from someone else: notification lands.
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            f"/api/reviews/{self.review.pk}/replies/", {"text": "agreed"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        note = Notification.objects.get(user=self.author, type="review_reply")
        self.assertEqual(note.data["text_preview"], "agreed")


class FavoritePlaceReviewFanOutTests(APITestCase):
    """Approving a review notifies everyone who favorited the place."""

    def setUp(self):
        self.reviewer = User.objects.create_user(
            email="rev-f@example.com", password="testpass123", username="revf"
        )
        self.fan = User.objects.create_user(
            email="fan@example.com", password="testpass123", username="fan"
        )
        self.banned_fan = User.objects.create_user(
            email="banned-f@example.com", password="testpass123", username="bannedf"
        )
        self.banned_fan.is_banned = True
        self.banned_fan.save(update_fields=["is_banned"])
        self.admin = User.objects.create_superuser(
            email="admin-f@example.com", password="testpass123", username="adminf"
        )
        self.place = make_place(self.reviewer, name="Fan Spot")
        for user in (self.fan, self.banned_fan, self.reviewer):
            PlaceFavorite.objects.create(user=user, place=self.place)
        self.review = Review.objects.create(
            place=self.place,
            author=self.reviewer,
            score=Decimal("9.0"),
            comment="great",
        )

    def _approve(self):
        self.client.force_authenticate(user=self.admin)
        return self.client.patch(
            f"/api/reviews/{self.review.pk}/approve/", {}, format="json"
        )

    def test_approval_notifies_fans_but_not_reviewer_or_banned(self):
        response = self._approve()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notes = Notification.objects.filter(type="favorite_place_review")
        self.assertEqual([n.user_id for n in notes], [self.fan.id])
        note = notes.get()
        self.assertEqual(note.data["place_name"], "Fan Spot")
        self.assertEqual(note.data["review_author"], "revf")

    def test_re_approval_does_not_duplicate(self):
        self._approve()
        self._approve()
        self.assertEqual(
            Notification.objects.filter(
                user=self.fan, type="favorite_place_review"
            ).count(),
            1,
        )
