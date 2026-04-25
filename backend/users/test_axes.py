"""Brute-force protection tests for the JWT login endpoint (django-axes)."""

from __future__ import annotations

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


_LOCKOUT_OVERRIDES = {
    "AXES_ENABLED": True,
    "AXES_FAILURE_LIMIT": 3,
    "AXES_RESET_ON_SUCCESS": True,
    "AXES_LOCKOUT_PARAMETERS": ["username", "ip_address"],
    # No cooloff so that the test doesn't depend on real wall clock.
    "AXES_COOLOFF_TIME": None,
    # Throttle high enough that the rate limiter doesn't 429 first.
    "REST_FRAMEWORK": {
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
    },
}


@override_settings(**_LOCKOUT_OVERRIDES)
class AxesLockoutTests(APITestCase):
    login_url = "/api/users/login/"

    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        # Reset axes state between tests (we use the in-process backend by
        # default, but be explicit to avoid bleed-over).
        from axes.utils import reset

        reset()
        self.user = User.objects.create_user(
            email="alice@example.com",
            password="StrongPass!234",
            first_name="Alice",
        )

    def _bad_login(self):
        return self.client.post(
            self.login_url,
            {"email": "alice@example.com", "password": "wrong"},
            format="json",
        )

    def test_lockout_after_failure_limit(self):
        from axes.models import AccessAttempt

        limit = 3
        for _ in range(limit):
            resp = self._bad_login()
            self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        # The user is now locked out: axes refuses authentication so the
        # JWT view can't issue a token even with the correct password.
        good = self.client.post(
            self.login_url,
            {"email": "alice@example.com", "password": "StrongPass!234"},
            format="json",
        )
        self.assertNotEqual(good.status_code, status.HTTP_200_OK)
        self.assertNotIn("access", good.json())

        # And axes recorded the failed attempts.
        self.assertTrue(
            AccessAttempt.objects.filter(username="alice@example.com").exists()
        )

    def test_successful_login_resets_counter(self):
        # Two failures, then a success — counter resets and a third
        # failure should NOT lock the account.
        self._bad_login()
        self._bad_login()
        good = self.client.post(
            self.login_url,
            {"email": "alice@example.com", "password": "StrongPass!234"},
            format="json",
        )
        self.assertEqual(good.status_code, status.HTTP_200_OK)

        bad = self._bad_login()
        self.assertEqual(bad.status_code, status.HTTP_401_UNAUTHORIZED)
