"""Tests for review replies and the public by-user reviews list."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from places.models import Place
from reviews.models import Review, ReviewReply

User = get_user_model()


def make_place(author):
    return Place.objects.create(
        name="Reply Spot",
        district="Unknown",
        address="Test Address",
        main_image="test.jpg",
        status="Active",
        author=author,
    )


class ReviewReplyTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            email="ra@example.com", password="testpass123", username="ra"
        )
        self.commenter = User.objects.create_user(
            email="rc@example.com", password="testpass123", username="rc"
        )
        self.place = make_place(self.author)
        self.review = Review.objects.create(
            place=self.place,
            author=self.author,
            score=Decimal("8.0"),
            comment="nice",
            is_moderated=True,
        )
        self.url = f"/api/reviews/{self.review.pk}/replies/"

    def test_anonymous_can_read_but_not_post(self):
        ReviewReply.objects.create(
            review=self.review, author=self.commenter, text="hello"
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["text"], "hello")
        post = self.client.post(self.url, {"text": "nope"})
        self.assertEqual(post.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_reply_and_replies_count(self):
        self.client.force_authenticate(user=self.commenter)
        response = self.client.post(self.url, {"text": "totally agree"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author_username"], "rc")
        listing = self.client.get(f"/api/places/{self.place.pk}/reviews/")
        row = next(r for r in listing.data["results"] if r["id"] == self.review.pk)
        self.assertEqual(row["replies_count"], 1)

    def test_replies_hidden_for_pending_review(self):
        pending = Review.objects.create(
            place=self.place, author=self.author, score=Decimal("6.0"), comment="wip"
        )
        url = f"/api/reviews/{pending.pk}/replies/"
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)
        # The review's own author still sees the thread.
        self.client.force_authenticate(user=self.author)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

    def test_delete_own_reply_only(self):
        reply = ReviewReply.objects.create(
            review=self.review, author=self.commenter, text="oops"
        )
        delete_url = f"/api/reviews/replies/{reply.pk}/"
        self.client.force_authenticate(user=self.author)
        self.assertEqual(
            self.client.delete(delete_url).status_code, status.HTTP_403_FORBIDDEN
        )
        self.client.force_authenticate(user=self.commenter)
        self.assertEqual(
            self.client.delete(delete_url).status_code, status.HTTP_204_NO_CONTENT
        )
        reply.refresh_from_db()
        self.assertTrue(reply.is_deleted)
        # Soft-deleted replies disappear from the list.
        listing = self.client.get(self.url)
        self.assertEqual(listing.data["results"], [])

    def test_reply_text_is_limited(self):
        self.client.force_authenticate(user=self.commenter)
        response = self.client.post(self.url, {"text": "x" * 1001})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserReviewsListTests(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            email="pub@example.com", password="testpass123", username="pub"
        )
        self.place = make_place(self.author)
        self.approved = Review.objects.create(
            place=self.place,
            author=self.author,
            score=Decimal("8.0"),
            comment="approved",
            is_moderated=True,
        )
        Review.objects.create(
            place=self.place, author=self.author, score=Decimal("6.0"), comment="wip"
        )
        self.url = f"/api/reviews/by-user/{self.author.pk}/"

    def test_lists_only_approved_reviews(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [row["id"] for row in response.data["results"]]
        self.assertEqual(ids, [self.approved.id])

    def test_banned_author_404s(self):
        self.author.is_banned = True
        self.author.save(update_fields=["is_banned"])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
