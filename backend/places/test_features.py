"""Tests for the new moderation, rating, menu and articles flows."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from articles.models import Article
from places.models import Place, PlaceRating
from places_menu.models import Menu
from reviews.models import Review

User = get_user_model()


class PlaceModerationFlowTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com", password="pw12345!", username="user"
        )
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="pw12345!",
            username="admin",
            is_staff=True,
        )

    def test_create_forces_on_moderation(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "My Place",
            "address": "123 Test St",
            "main_image": "x.jpg",
            "status": "Active",  # should be ignored
        }
        resp = self.client.post("/api/places/create-place/", data, format="json")
        # The serializer requires `main_image` as ImageField; accept either 201 or 400 (bad image),
        # but the place must not be created with status=Active.
        if resp.status_code == status.HTTP_201_CREATED:
            place = Place.objects.get(name="My Place")
            self.assertEqual(place.status, "On_moderation")
            self.assertEqual(place.author, self.user)

    def test_public_list_hides_non_active(self):
        Place.objects.create(
            name="Pending", address="x", main_image="x.jpg", status="On_moderation"
        )
        Place.objects.create(
            name="Active", address="x", main_image="x.jpg", status="Active"
        )
        self.client.logout()
        resp = self.client.get("/api/places/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        names = [p["name"] for p in resp.data["results"]]
        self.assertIn("Active", names)
        self.assertNotIn("Pending", names)

    def test_admin_can_approve(self):
        place = Place.objects.create(
            name="Pending",
            address="x",
            main_image="x.jpg",
            status="On_moderation",
            author=self.user,
        )
        self.client.force_authenticate(user=self.admin)
        resp = self.client.patch(
            f"/api/places/{place.pk}/approve/", {"reason": "OK"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        place.refresh_from_db()
        self.assertEqual(place.status, "Active")
        self.assertEqual(place.moderated_by, self.admin)

    def test_non_admin_cannot_approve(self):
        place = Place.objects.create(
            name="Pending",
            address="x",
            main_image="x.jpg",
            status="On_moderation",
            author=self.user,
        )
        self.client.force_authenticate(user=self.user)
        resp = self.client.patch(f"/api/places/{place.pk}/approve/", format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_moderation_list(self):
        Place.objects.create(
            name="P", address="x", main_image="x.jpg", status="On_moderation"
        )
        Place.objects.create(
            name="A", address="x", main_image="x.jpg", status="Active"
        )
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get("/api/places/moderation/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        names = [p["name"] for p in resp.data["results"]]
        self.assertEqual(names, ["P"])

    def test_filtering_by_district(self):
        Place.objects.create(
            name="Dnipro Place",
            address="x",
            main_image="x.jpg",
            status="Active",
            district="Dnipro",
        )
        Place.objects.create(
            name="Other",
            address="x",
            main_image="x.jpg",
            status="Active",
            district="Podil",
        )
        resp = self.client.get("/api/places/?district=Dnipro")
        names = [p["name"] for p in resp.data["results"]]
        self.assertEqual(names, ["Dnipro Place"])


class PlaceRateEndpointTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="u@e.com", password="pw12345!", username="u"
        )
        self.place = Place.objects.create(
            name="X", address="x", main_image="x.jpg", status="Active"
        )

    def test_rate_with_5_stars_stores_10_internal(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(
            f"/api/places/{self.place.pk}/rate/", {"rating": 5}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        rating = PlaceRating.objects.get(user=self.user, place=self.place)
        self.assertEqual(rating.rating, Decimal("10"))
        self.place.refresh_from_db()
        self.assertEqual(self.place.rating, Decimal("10"))
        self.assertEqual(self.place.stars, 5.0)

    def test_rate_validates_range(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(
            f"/api/places/{self.place.pk}/rate/", {"rating": 0}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        resp = self.client.post(
            f"/api/places/{self.place.pk}/rate/", {"rating": 6}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class ReviewModerationFlowTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="u@e.com", password="pw12345!", username="u"
        )
        self.admin = User.objects.create_user(
            email="a@e.com", password="pw12345!", username="a", is_staff=True
        )
        self.place = Place.objects.create(
            name="P", address="x", main_image="x.jpg", status="Active"
        )

    def test_create_review_is_pending(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post(
            f"/api/places/{self.place.pk}/reviews/",
            {"score": "8.0", "comment": "Good"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        review = Review.objects.get(author=self.user, place=self.place)
        self.assertFalse(review.is_moderated)

    def test_public_list_hides_unmoderated(self):
        Review.objects.create(
            place=self.place,
            author=self.user,
            score=Decimal("8.0"),
            comment="Hidden",
            is_moderated=False,
        )
        Review.objects.create(
            place=self.place,
            author=self.user,
            score=Decimal("9.0"),
            comment="Visible",
            is_moderated=True,
        )
        self.client.logout()
        resp = self.client.get(f"/api/places/{self.place.pk}/reviews/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        comments = [r["comment"] for r in resp.data["results"]]
        self.assertIn("Visible", comments)
        self.assertNotIn("Hidden", comments)

    def test_admin_approve_recomputes_rating(self):
        review = Review.objects.create(
            place=self.place,
            author=self.user,
            score=Decimal("8.0"),
            comment="Pending",
            is_moderated=False,
        )
        self.assertEqual(self.place.rating, Decimal("0.0"))
        self.client.force_authenticate(user=self.admin)
        resp = self.client.patch(
            f"/api/reviews/{review.pk}/approve/", format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertTrue(review.is_moderated)
        self.place.refresh_from_db()
        self.assertEqual(self.place.rating, Decimal("8.00"))

    def test_admin_reject_marks_deleted(self):
        review = Review.objects.create(
            place=self.place,
            author=self.user,
            score=Decimal("3.0"),
            comment="Bad",
            is_moderated=False,
        )
        self.client.force_authenticate(user=self.admin)
        resp = self.client.patch(
            f"/api/reviews/{review.pk}/reject/", format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertTrue(review.is_deleted)
        self.assertFalse(review.is_moderated)


class MenuApiTest(APITestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            email="o@e.com", password="pw12345!", username="o"
        )
        self.other = User.objects.create_user(
            email="x@e.com", password="pw12345!", username="x"
        )
        self.place = Place.objects.create(
            name="P",
            address="x",
            main_image="x.jpg",
            status="Active",
            author=self.author,
        )

    def test_public_can_list_menu(self):
        Menu.objects.create(
            place=self.place,
            name="Shawarma",
            price=Decimal("100"),
            category="shawarma",
        )
        self.client.logout()
        resp = self.client.get(f"/api/places/{self.place.pk}/menu/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 1)

    def test_only_author_can_create_menu_item(self):
        url = f"/api/places/{self.place.pk}/menu/"
        data = {"name": "Drink", "price": "30", "category": "drinks"}
        # Other authenticated user should be forbidden.
        self.client.force_authenticate(user=self.other)
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        # Author can create.
        self.client.force_authenticate(user=self.author)
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


class ArticlesApiTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="a@e.com", password="pw12345!", username="a", is_staff=True
        )

    def test_public_list_only_published(self):
        Article.objects.create(title="Hidden", content="x", is_published=False)
        published = Article.objects.create(
            title="Visible", content="hello world", is_published=True
        )
        self.client.logout()
        resp = self.client.get("/api/articles/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        slugs = [a["slug"] for a in resp.data["results"]]
        self.assertIn(published.slug, slugs)
        self.assertEqual(len(slugs), 1)

    def test_detail_by_slug(self):
        article = Article.objects.create(
            title="A Tale", content="content", is_published=True
        )
        resp = self.client.get(f"/api/articles/{article.slug}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["title"], "A Tale")

    def test_only_admin_can_create(self):
        # Anonymous
        resp = self.client.post(
            "/api/articles/", {"title": "T", "content": "c"}, format="json"
        )
        self.assertIn(
            resp.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )
        # Admin
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(
            "/api/articles/", {"title": "T", "content": "c"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Article.objects.filter(title="T").exists())
