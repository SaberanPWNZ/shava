"""Tests for the cities catalogue (model, seed_cities, ?city= filter)."""

from __future__ import annotations

import io
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import CommandError, call_command
from django.test import TestCase
from django.urls import reverse

from places.models import City, Place


class SeedCitiesCommandTests(TestCase):
    def test_default_csv_seeds_known_cities(self):
        out = io.StringIO()
        call_command("seed_cities", stdout=out)
        self.assertTrue(City.objects.filter(slug="kyiv").exists())
        self.assertTrue(City.objects.filter(slug="lviv").exists())
        self.assertIn("created=", out.getvalue())

    def test_command_is_idempotent(self):
        call_command("seed_cities")
        first = City.objects.count()
        call_command("seed_cities")
        self.assertEqual(City.objects.count(), first)

    def test_custom_csv_with_missing_columns_errors(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.csv"
            path.write_text("name,region\nKyiv,UA\n", encoding="utf-8")
            with self.assertRaises(CommandError):
                call_command("seed_cities", file=str(path))

    def test_deactivate_missing(self):
        City.objects.create(name="Atlantis", slug="atlantis")
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "small.csv"
            path.write_text("name,slug,region\nKyiv,kyiv,UA\n", encoding="utf-8")
            call_command("seed_cities", file=str(path), deactivate_missing=True)
        atlantis = City.objects.get(slug="atlantis")
        self.assertFalse(atlantis.is_active)


class PlaceCityFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.kyiv, _ = City.objects.get_or_create(slug="kyiv", defaults={"name": "Київ"})
        cls.lviv, _ = City.objects.get_or_create(
            slug="lviv", defaults={"name": "Львів"}
        )
        # Two places: one tied to Kyiv via FK, one to Lviv via the legacy
        # CharField only (city_ref left NULL).
        cls.p_kyiv = Place.objects.create(
            name="Шава А",
            city="Київ",
            city_ref=cls.kyiv,
            address="вул. Хрещатик 1",
            status="Active",
            main_image="x.jpg",
        )
        cls.p_lviv = Place.objects.create(
            name="Шава Б",
            city="Львів",
            address="пл. Ринок 2",
            status="Approved",
            main_image="x.jpg",
        )

    def test_filter_by_slug(self):
        url = reverse("places-list") + "?city=kyiv"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        names = {p["name"] for p in resp.json()["results"]}
        self.assertEqual(names, {"Шава А"})

    def test_filter_by_city_id(self):
        url = reverse("places-list") + f"?city={self.kyiv.id}"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        names = {p["name"] for p in resp.json()["results"]}
        self.assertEqual(names, {"Шава А"})

    def test_filter_by_legacy_charfield_name(self):
        url = reverse("places-list") + "?city=Львів"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        names = {p["name"] for p in resp.json()["results"]}
        self.assertEqual(names, {"Шава Б"})

    def test_filter_unknown_city_returns_empty(self):
        url = reverse("places-list") + "?city=atlantis"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["results"], [])


class CityListViewTests(TestCase):
    """``GET /places/cities/`` — public, unpaginated, active-only list."""

    @classmethod
    def setUpTestData(cls):
        cls.kyiv, _ = City.objects.get_or_create(slug="kyiv", defaults={"name": "Київ"})
        cls.lviv, _ = City.objects.get_or_create(
            slug="lviv", defaults={"name": "Львів"}
        )
        City.objects.create(name="Retired Town", slug="retired-town", is_active=False)

    def test_anonymous_can_list_cities(self):
        url = reverse("places-cities")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_response_is_unpaginated_list(self):
        url = reverse("places-cities")
        resp = self.client.get(url)
        self.assertIsInstance(resp.json(), list)

    def test_excludes_inactive_cities(self):
        url = reverse("places-cities")
        resp = self.client.get(url)
        slugs = {c["slug"] for c in resp.json()}
        self.assertIn("kyiv", slugs)
        self.assertNotIn("retired-town", slugs)

    def test_entries_expose_minimal_shape(self):
        url = reverse("places-cities")
        resp = self.client.get(url)
        entry = next(c for c in resp.json() if c["slug"] == "kyiv")
        self.assertEqual(set(entry.keys()), {"id", "name", "slug"})
