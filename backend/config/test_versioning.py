"""Tests for the API versioning roll-out (Roadmap 3.2).

Two invariants:

1. Every public endpoint resolves under both the new ``/api/v1/`` mount
   and the legacy ``/api/`` mount.
2. Responses served from the legacy mount carry RFC 9745 / RFC 8594
   headers (``Deprecation``, ``Sunset``, ``Link``); responses served
   from ``/api/v1/`` do **not**.
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase

User = get_user_model()

NO_THROTTLE: dict = {"DEFAULT_THROTTLE_RATES": {}, "DEFAULT_THROTTLE_CLASSES": []}


@override_settings(AXES_ENABLED=False)
class ApiVersioningTests(APITestCase):
    """Use the unauthenticated, no-state badge catalogue as a probe."""

    LEGACY = "/api/gamification/badges/"
    VERSIONED = "/api/v1/gamification/badges/"

    def test_versioned_route_resolves(self):
        resp = self.client.get(self.VERSIONED)
        self.assertEqual(resp.status_code, 200)

    def test_legacy_route_still_resolves(self):
        resp = self.client.get(self.LEGACY)
        self.assertEqual(resp.status_code, 200)

    def test_legacy_route_carries_deprecation_headers(self):
        resp = self.client.get(self.LEGACY)
        self.assertEqual(resp["Deprecation"], "true")
        self.assertIn("Sunset", resp)
        self.assertIn('rel="successor-version"', resp["Link"])
        self.assertIn(self.VERSIONED, resp["Link"])

    def test_versioned_route_has_no_deprecation_headers(self):
        resp = self.client.get(self.VERSIONED)
        self.assertNotIn("Deprecation", resp)
        self.assertNotIn("Sunset", resp)
        self.assertNotIn("Link", resp)

    def test_unrelated_admin_path_unaffected(self):
        # /admin/ is outside /api/, so the middleware must leave it alone.
        resp = self.client.get("/admin/login/")
        self.assertNotIn("Deprecation", resp)


@override_settings(AXES_ENABLED=False)
class ApiVersioningAuthedTests(APITestCase):
    """Sanity-check a *real* authed JSON endpoint on both mounts."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="vivi",
            email="vivi@example.com",
            password="strongpass123",
            is_verified=True,
        )
        self.client.force_authenticate(self.user)

    def test_users_me_resolves_under_v1(self):
        resp = self.client.get("/api/v1/users/me/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["email"], "vivi@example.com")
        self.assertNotIn("Deprecation", resp)

    def test_users_me_resolves_under_legacy(self):
        resp = self.client.get("/api/users/me/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["email"], "vivi@example.com")
        self.assertEqual(resp["Deprecation"], "true")
