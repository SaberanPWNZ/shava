"""Query-count regression tests for list endpoints (ROADMAP 4.2).

These tests assert that the public list endpoints stay at a constant
small number of SQL queries regardless of how many rows the page
contains. They are the executable contract behind the annotations and
``select_related`` calls in :mod:`places.views`, :mod:`reviews.views`
and :mod:`articles.views`.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test.utils import CaptureQueriesContext
from django.db import connection
from rest_framework import status
from rest_framework.test import APITestCase

from articles.models import Article
from places.models import Place, PlaceRating
from reviews.models import Review

User = get_user_model()


# Constant query budget per list endpoint, regardless of page size.
# A small upper bound that catches the obvious N+1 regressions while
# tolerating the framework overhead (SAVEPOINT/RELEASE under
# ``APITestCase`` plus ``COUNT(*)`` from DRF pagination wrappers).
LIST_QUERY_BUDGET = 6


class PlaceListQueryCountTests(APITestCase):
    """`/api/places/` must not issue per-row queries."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            email="a@example.com", password="pw12345!", username="a"
        )
        cls.rater = User.objects.create_user(
            email="r@example.com", password="pw12345!", username="r"
        )
        # Two visible places with ratings + approved reviews + one extra
        # rejected/deleted review each. If serialization re-queries per
        # row, a second/third place doubles/triples the query count.
        cls.places = []
        for i in range(3):
            place = Place.objects.create(
                name=f"Place {i}",
                city="Київ",
                address=f"Addr {i}",
                main_image="x.jpg",
                status="Active",
                author=cls.author,
            )
            PlaceRating.objects.create(
                user=cls.rater, place=place, rating=Decimal("8.0")
            )
            Review.objects.create(
                place=place,
                author=cls.rater,
                score=Decimal("9.0"),
                comment="ok",
                is_moderated=True,
            )
            Review.objects.create(
                place=place,
                author=cls.rater,
                score=Decimal("3.0"),
                comment="hidden",
                is_moderated=False,
            )
            cls.places.append(place)

    def test_query_count_is_constant_for_three_rows(self):
        # Warm up any lazy app-loading work first.
        self.client.get("/api/places/")
        with CaptureQueriesContext(connection) as ctx:
            resp = self.client.get("/api/places/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.json().get("results", resp.json())), 3)
        self.assertLessEqual(
            len(ctx.captured_queries),
            LIST_QUERY_BUDGET,
            f"Too many queries on /api/places/ list: {len(ctx.captured_queries)}\n"
            + "\n".join(q["sql"] for q in ctx.captured_queries),
        )

    def test_query_count_does_not_grow_with_page_size(self):
        # Add 7 more places (total 10) and expect the query count to
        # stay at the same budget.
        for i in range(3, 10):
            place = Place.objects.create(
                name=f"Place {i}",
                city="Київ",
                address=f"Addr {i}",
                main_image="x.jpg",
                status="Active",
                author=self.author,
            )
            PlaceRating.objects.create(
                user=self.rater, place=place, rating=Decimal("7.0")
            )
            Review.objects.create(
                place=place,
                author=self.rater,
                score=Decimal("8.0"),
                comment="ok",
                is_moderated=True,
            )
        self.client.get("/api/places/")  # warm up
        with CaptureQueriesContext(connection) as ctx:
            resp = self.client.get("/api/places/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertLessEqual(
            len(ctx.captured_queries),
            LIST_QUERY_BUDGET,
            "Query count grew with page size — N+1 regression",
        )


class ReviewListQueryCountTests(APITestCase):
    """`/api/places/<id>/reviews/` and `/api/reviews/` query budgets."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="u@example.com", password="pw12345!", username="u"
        )
        cls.place = Place.objects.create(
            name="P",
            city="Київ",
            address="x",
            main_image="x.jpg",
            status="Active",
        )
        # 5 approved reviews from 5 different authors. If we don't
        # `select_related("author")`, `author_username` triggers a
        # SELECT per review.
        for i in range(5):
            author = User.objects.create_user(
                email=f"a{i}@example.com", password="pw12345!", username=f"a{i}"
            )
            Review.objects.create(
                place=cls.place,
                author=author,
                score=Decimal("8.0"),
                comment=f"r{i}",
                is_moderated=True,
            )

    def test_place_reviews_list_query_budget(self):
        url = f"/api/places/{self.place.id}/reviews/"
        self.client.get(url)  # warm up
        with CaptureQueriesContext(connection) as ctx:
            resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        body = resp.json()
        items = body["results"] if isinstance(body, dict) and "results" in body else body
        self.assertEqual(len(items), 5)
        self.assertLessEqual(
            len(ctx.captured_queries),
            LIST_QUERY_BUDGET,
            f"Too many queries on /api/places/<id>/reviews/: "
            f"{len(ctx.captured_queries)}",
        )

    def test_my_reviews_list_query_budget(self):
        # `ReviewViewSet` is registered as `my-reviews` under
        # `/api/reviews/`, so the actual URL is `/api/reviews/my-reviews/`.
        Review.objects.create(
            place=self.place,
            author=self.user,
            score=Decimal("9.0"),
            comment="mine",
            is_moderated=True,
        )
        self.client.force_authenticate(user=self.user)
        url = "/api/reviews/my-reviews/"
        self.client.get(url)  # warm up
        with CaptureQueriesContext(connection) as ctx:
            resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertLessEqual(
            len(ctx.captured_queries),
            LIST_QUERY_BUDGET,
            "Too many queries on /api/reviews/my-reviews/",
        )


class ArticleListQueryCountTests(APITestCase):
    """`/api/articles/` should join the author in a single SELECT."""

    @classmethod
    def setUpTestData(cls):
        for i in range(5):
            author = User.objects.create_user(
                email=f"author{i}@example.com",
                password="pw12345!",
                username=f"author{i}",
            )
            Article.objects.create(
                title=f"Article {i}",
                slug=f"article-{i}",
                excerpt="x",
                content="y",
                category="news",
                author=author,
                is_published=True,
            )

    def test_articles_list_query_budget(self):
        self.client.get("/api/articles/")  # warm up
        with CaptureQueriesContext(connection) as ctx:
            resp = self.client.get("/api/articles/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertLessEqual(
            len(ctx.captured_queries),
            LIST_QUERY_BUDGET,
            f"Too many queries on /api/articles/: {len(ctx.captured_queries)}",
        )
