"""Tests for the users app: registration, login, refresh, me, change password,
logout, throttling, and privilege-escalation guards."""
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


# Disable throttling for most tests so they don't interfere; throttling has
# its own dedicated test below.
NO_THROTTLE = {
    "DEFAULT_THROTTLE_RATES": {
        "auth": "1000/min",
        "register": "1000/min",
    },
}


@override_settings(REST_FRAMEWORK={**NO_THROTTLE, **{
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
    ],
}})
class AuthFlowTests(APITestCase):
    register_url = "/api/users/register/"
    login_url = "/api/users/login/"
    refresh_url = "/api/users/token/refresh/"
    me_url = "/api/users/me/"
    change_password_url = "/api/users/me/change-password/"
    logout_url = "/api/users/logout/"

    def setUp(self):
        from django.core.cache import cache

        cache.clear()

    def _register(self, email="alice@example.com", password="StrongPass!234"):
        return self.client.post(
            self.register_url,
            {"email": email, "password": password, "first_name": "Alice"},
            format="json",
        )

    def _login(self, email="alice@example.com", password="StrongPass!234"):
        return self.client.post(
            self.login_url, {"email": email, "password": password}, format="json"
        )

    def test_register_creates_user_and_hides_sensitive_fields(self):
        response = self._register()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)
        self.assertNotIn("is_staff", response.data)
        self.assertNotIn("is_superuser", response.data)
        self.assertNotIn("is_admin", response.data)

        user = User.objects.get(email="alice@example.com")
        self.assertTrue(user.check_password("StrongPass!234"))

    def test_register_ignores_privileged_fields(self):
        """Privilege-escalation guard: extra ``is_*`` payload must be ignored."""
        response = self.client.post(
            self.register_url,
            {
                "email": "eve@example.com",
                "password": "StrongPass!234",
                "is_staff": True,
                "is_superuser": True,
                "is_admin": True,
                "is_moderator": True,
                "is_verified": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="eve@example.com")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_moderator)
        self.assertFalse(user.is_verified)

    def test_register_rejects_weak_password(self):
        response = self.client.post(
            self.register_url,
            {"email": "weak@example.com", "password": "123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_register_rejects_duplicate_email_case_insensitive(self):
        self._register()
        response = self._register(email="ALICE@example.com")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_login_returns_tokens(self):
        self._register()
        response = self._login()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_rotates_token(self):
        self._register()
        login = self._login()
        refresh = login.data["refresh"]
        response = self.client.post(
            self.refresh_url, {"refresh": refresh}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_me_requires_auth(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_get_and_patch(self):
        self._register()
        access = self._login().data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        get_resp = self.client.get(self.me_url)
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(get_resp.data["email"], "alice@example.com")

        patch_resp = self.client.patch(
            self.me_url, {"first_name": "Alicia"}, format="json"
        )
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_resp.data["first_name"], "Alicia")

    def test_me_patch_cannot_escalate_privileges(self):
        self._register()
        access = self._login().data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.patch(
            self.me_url,
            {"is_staff": True, "is_admin": True, "email": "evil@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(email="alice@example.com")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_admin)
        self.assertEqual(user.email, "alice@example.com")

    def test_change_password_flow(self):
        self._register()
        access = self._login().data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        wrong = self.client.post(
            self.change_password_url,
            {"old_password": "wrong", "new_password": "AnotherStrong!234"},
            format="json",
        )
        self.assertEqual(wrong.status_code, status.HTTP_400_BAD_REQUEST)

        ok = self.client.post(
            self.change_password_url,
            {
                "old_password": "StrongPass!234",
                "new_password": "AnotherStrong!234",
            },
            format="json",
        )
        self.assertEqual(ok.status_code, status.HTTP_204_NO_CONTENT)

        # New password works for login
        self.client.credentials()
        login = self._login(password="AnotherStrong!234")
        self.assertEqual(login.status_code, status.HTTP_200_OK)

    def test_logout_blacklists_refresh_token(self):
        self._register()
        login = self._login()
        access, refresh = login.data["access"], login.data["refresh"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        logout = self.client.post(
            self.logout_url, {"refresh": refresh}, format="json"
        )
        self.assertEqual(logout.status_code, status.HTTP_205_RESET_CONTENT)

        # The blacklisted refresh token can no longer be used.
        self.client.credentials()
        refresh_resp = self.client.post(
            self.refresh_url, {"refresh": refresh}, format="json"
        )
        self.assertEqual(refresh_resp.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(REST_FRAMEWORK={
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"auth": "2/min", "register": "2/min"},
})
class ThrottlingTests(APITestCase):
    def setUp(self):
        from django.core.cache import cache
        from rest_framework.throttling import SimpleRateThrottle
        from rest_framework.settings import api_settings

        cache.clear()
        # ``SimpleRateThrottle.THROTTLE_RATES`` is captured at class definition
        # time, so ``override_settings`` alone does not propagate. Patch the
        # class attribute for the duration of the test.
        self._original_rates = SimpleRateThrottle.THROTTLE_RATES
        SimpleRateThrottle.THROTTLE_RATES = api_settings.DEFAULT_THROTTLE_RATES

    def tearDown(self):
        from rest_framework.throttling import SimpleRateThrottle

        SimpleRateThrottle.THROTTLE_RATES = self._original_rates

    def test_login_is_throttled(self):
        User.objects.create_user(email="bob@example.com", password="StrongPass!234")
        url = "/api/users/login/"
        for _ in range(2):
            self.client.post(
                url,
                {"email": "bob@example.com", "password": "StrongPass!234"},
                format="json",
            )
        third = self.client.post(
            url,
            {"email": "bob@example.com", "password": "StrongPass!234"},
            format="json",
        )
        self.assertEqual(third.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


@override_settings(REST_FRAMEWORK={
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "users.authentication.BanAwareJWTAuthentication",
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
    },
})
class UserBanTests(APITestCase):
    """Ban/unban admin endpoints and authentication guard."""

    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="AdminPass!234",
            is_staff=True,
            is_superuser=True,
        )
        self.target = User.objects.create_user(
            email="target@example.com", password="TargetPass!234"
        )
        self.regular = User.objects.create_user(
            email="regular@example.com", password="RegularPass!234"
        )

    def _login(self, email, password):
        resp = self.client.post(
            "/api/users/login/", {"email": email, "password": password}, format="json"
        )
        self.assertEqual(resp.status_code, 200, resp.data)
        return resp.data["access"]

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_ban_endpoint_requires_admin(self):
        token = self._login("regular@example.com", "RegularPass!234")
        self._auth(token)
        resp = self.client.post(f"/api/users/{self.target.pk}/ban/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_ban_and_unban_user(self):
        token = self._login("admin@example.com", "AdminPass!234")
        self._auth(token)

        resp = self.client.post(f"/api/users/{self.target.pk}/ban/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)
        self.target.refresh_from_db()
        self.assertTrue(self.target.is_banned)

        resp = self.client.post(f"/api/users/{self.target.pk}/unban/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.target.refresh_from_db()
        self.assertFalse(self.target.is_banned)

    def test_admin_cannot_ban_self(self):
        token = self._login("admin@example.com", "AdminPass!234")
        self._auth(token)
        resp = self.client.post(f"/api/users/{self.admin.pk}/ban/")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_banned_user_cannot_login(self):
        self.target.is_banned = True
        self.target.save(update_fields=["is_banned"])
        resp = self.client.post(
            "/api/users/login/",
            {"email": "target@example.com", "password": "TargetPass!234"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_banned_user_existing_token_is_rejected(self):
        token = self._login("target@example.com", "TargetPass!234")
        self.target.is_banned = True
        self.target.save(update_fields=["is_banned"])
        self._auth(token)
        resp = self.client.get("/api/users/me/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
