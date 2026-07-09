"""Tests for HttpOnly-cookie JWT delivery and authentication."""

from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from users.cookies import ACCESS_COOKIE, REFRESH_COOKIE
from users.tests.tests import NO_THROTTLE

User = get_user_model()

LOGIN_URL = "/api/users/login/"
REFRESH_URL = "/api/users/token/refresh/"
LOGOUT_URL = "/api/users/logout/"
ME_URL = "/api/users/me/"

EMAIL = "cookie@example.com"
PASSWORD = "Str0ng!passw0rd"


@override_settings(
    REST_FRAMEWORK={
        **NO_THROTTLE,
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "users.authentication.BanAwareJWTAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": [
            "rest_framework.permissions.IsAuthenticated",
        ],
        "DEFAULT_THROTTLE_CLASSES": [
            "rest_framework.throttling.ScopedRateThrottle",
        ],
    }
)
class CookieAuthTests(APITestCase):
    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.user = User.objects.create_user(email=EMAIL, password=PASSWORD)

    def _login(self):
        return self.client.post(
            LOGIN_URL, {"email": EMAIL, "password": PASSWORD}, format="json"
        )

    def test_login_sets_httponly_cookies(self):
        response = self._login()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for name in (ACCESS_COOKIE, REFRESH_COOKIE):
            cookie = response.cookies.get(name)
            self.assertIsNotNone(cookie, name)
            self.assertTrue(cookie["httponly"], name)
            self.assertEqual(cookie["samesite"], "Lax", name)
        # Body still carries the pair for non-browser clients.
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_cookie_authenticates_request_without_header(self):
        self._login()
        # APITestCase client keeps response cookies; no Authorization header.
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], EMAIL)

    def test_refresh_from_cookie_rotates_pair(self):
        login = self._login()
        old_refresh = login.cookies[REFRESH_COOKIE].value
        response = self.client.post(REFRESH_URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_refresh = response.cookies.get(REFRESH_COOKIE)
        self.assertIsNotNone(new_refresh)
        self.assertNotEqual(new_refresh.value, old_refresh)
        # The rotated-out token is blacklisted.
        self.client.cookies[REFRESH_COOKIE] = old_refresh
        retry = self.client.post(REFRESH_URL, {}, format="json")
        self.assertEqual(retry.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_with_invalid_cookie_clears_cookies(self):
        self.client.cookies[REFRESH_COOKIE] = "garbage"
        response = self.client.post(REFRESH_URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.cookies[REFRESH_COOKIE].value, "")

    def test_logout_from_cookie_blacklists_and_clears(self):
        login = self._login()
        refresh = login.cookies[REFRESH_COOKIE].value
        response = self.client.post(LOGOUT_URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        self.assertEqual(response.cookies[ACCESS_COOKIE].value, "")
        self.assertEqual(response.cookies[REFRESH_COOKIE].value, "")
        self.client.cookies[REFRESH_COOKIE] = refresh
        retry = self.client.post(REFRESH_URL, {}, format="json")
        self.assertEqual(retry.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bearer_header_still_works(self):
        login = self._login()
        self.client.cookies.clear()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
