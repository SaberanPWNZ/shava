"""Tests for the users app: registration, login, refresh, me, change password,
logout, throttling, and privilege-escalation guards."""

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from places.models import City
from users.models import User

NO_THROTTLE = {
    "DEFAULT_THROTTLE_RATES": {
        "auth": "1000/min",
        "register": "1000/min",
    },
}


@override_settings(
    REST_FRAMEWORK={
        **NO_THROTTLE,
        **{
            "DEFAULT_AUTHENTICATION_CLASSES": [
                "rest_framework_simplejwt.authentication.JWTAuthentication",
            ],
            "DEFAULT_PERMISSION_CLASSES": [
                "rest_framework.permissions.IsAuthenticated",
            ],
            "DEFAULT_THROTTLE_CLASSES": [
                "rest_framework.throttling.ScopedRateThrottle",
            ],
        },
    }
)
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
            {
                "email": email,
                "password": password,
                "first_name": "Alice",
                "terms_accepted": True,
            },
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
                "terms_accepted": True,
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

        self.client.credentials()
        login = self._login(password="AnotherStrong!234")
        self.assertEqual(login.status_code, status.HTTP_200_OK)

    def test_logout_blacklists_refresh_token(self):
        self._register()
        login = self._login()
        access, refresh = login.data["access"], login.data["refresh"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        logout = self.client.post(self.logout_url, {"refresh": refresh}, format="json")
        self.assertEqual(logout.status_code, status.HTTP_205_RESET_CONTENT)

        self.client.credentials()
        refresh_resp = self.client.post(
            self.refresh_url, {"refresh": refresh}, format="json"
        )
        self.assertEqual(refresh_resp.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(
    REST_FRAMEWORK={
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
    }
)
class ThrottlingTests(APITestCase):
    def setUp(self):
        from django.core.cache import cache
        from rest_framework.settings import api_settings
        from rest_framework.throttling import SimpleRateThrottle

        cache.clear()
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


@override_settings(
    REST_FRAMEWORK={
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
    }
)
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


class UserListPermissionTests(APITestCase):
    """Guards against user enumeration / email harvesting via ``/users/list/``.

    ``IsSelfOrAdmin`` only implements ``has_object_permission``, which is
    never invoked for the ``list`` action — so the collection endpoint must
    be gated by an admin-level ``has_permission`` check instead.
    """

    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="AdminPass!234",
            is_staff=True,
            is_superuser=True,
        )
        self.regular = User.objects.create_user(
            email="regular@example.com", password="RegularPass!234"
        )
        self.other = User.objects.create_user(
            email="other@example.com", password="OtherPass!234"
        )

    def _login(self, email, password):
        resp = self.client.post(
            "/api/users/login/", {"email": email, "password": password}, format="json"
        )
        self.assertEqual(resp.status_code, 200, resp.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")

    def test_regular_user_cannot_list_users(self):
        self._login("regular@example.com", "RegularPass!234")
        resp = self.client.get("/api/users/list/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_list_users(self):
        resp = self.client.get("/api/users/list/")
        self.assertIn(
            resp.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_admin_can_list_users(self):
        self._login("admin@example.com", "AdminPass!234")
        resp = self.client.get("/api/users/list/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_regular_user_can_retrieve_self(self):
        self._login("regular@example.com", "RegularPass!234")
        resp = self.client.get(f"/api/users/{self.regular.pk}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_regular_user_cannot_retrieve_other(self):
        self._login("regular@example.com", "RegularPass!234")
        resp = self.client.get(f"/api/users/{self.other.pk}/")
        self.assertIn(
            resp.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
        )


@override_settings(
    REST_FRAMEWORK={
        **NO_THROTTLE,
        **{
            "DEFAULT_AUTHENTICATION_CLASSES": [
                "rest_framework_simplejwt.authentication.JWTAuthentication",
            ],
            "DEFAULT_PERMISSION_CLASSES": [
                "rest_framework.permissions.IsAuthenticated",
            ],
            "DEFAULT_THROTTLE_CLASSES": [
                "rest_framework.throttling.ScopedRateThrottle",
            ],
        },
    }
)
class RegistrationExtraFieldsTests(APITestCase):
    """Registration with the new phone/city/terms/marketing fields."""

    register_url = "/api/users/register/"

    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        # Distinct slug from the ones seeded by the 0007 data migration
        # (real city names), so this test is independent of seed data.
        self.city = City.objects.create(name="Test City", slug="test-city-kyiv")

    def _payload(self, **overrides):
        payload = {
            "email": "newbie@example.com",
            "password": "StrongPass!234",
            "first_name": "New",
            "terms_accepted": True,
        }
        payload.update(overrides)
        return payload

    def test_register_without_terms_accepted_is_rejected(self):
        payload = self._payload()
        del payload["terms_accepted"]
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("terms_accepted", response.data)
        self.assertFalse(User.objects.filter(email="newbie@example.com").exists())

    def test_register_with_terms_declined_is_rejected(self):
        response = self.client.post(
            self.register_url, self._payload(terms_accepted=False), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("terms_accepted", response.data)

    def test_register_stamps_terms_accepted_at(self):
        response = self.client.post(self.register_url, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="newbie@example.com")
        self.assertIsNotNone(user.terms_accepted_at)

    def test_register_with_valid_phone_and_city(self):
        response = self.client.post(
            self.register_url,
            self._payload(
                phone="+380501234567", city=self.city.pk, marketing_opt_in=True
            ),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        user = User.objects.get(email="newbie@example.com")
        self.assertEqual(user.phone, "+380501234567")
        self.assertEqual(user.city_id, self.city.pk)
        self.assertTrue(user.marketing_opt_in)

    def test_register_rejects_invalid_phone(self):
        response = self.client.post(
            self.register_url, self._payload(phone="not-a-phone"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone", response.data)

    def test_register_rejects_inactive_city(self):
        inactive = City.objects.create(
            name="Ghost Town", slug="ghost-town", is_active=False
        )
        response = self.client.post(
            self.register_url, self._payload(city=inactive.pk), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("city", response.data)

    def test_register_ignores_terms_accepted_at_override_attempt(self):
        """``terms_accepted_at`` must always be server-stamped, never client-supplied."""
        response = self.client.post(
            self.register_url,
            self._payload(terms_accepted_at="2000-01-01T00:00:00Z"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="newbie@example.com")
        self.assertGreater(user.terms_accepted_at.year, 2000)


@override_settings(
    REST_FRAMEWORK={
        **NO_THROTTLE,
        **{
            "DEFAULT_AUTHENTICATION_CLASSES": [
                "rest_framework_simplejwt.authentication.JWTAuthentication",
            ],
            "DEFAULT_PERMISSION_CLASSES": [
                "rest_framework.permissions.IsAuthenticated",
            ],
            "DEFAULT_THROTTLE_CLASSES": [
                "rest_framework.throttling.ScopedRateThrottle",
            ],
        },
    }
)
class MeUpdateExtraFieldsTests(APITestCase):
    """Self-service profile updates for the new fields."""

    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.city = City.objects.create(name="Test City", slug="test-city-lviv")
        self.user = User.objects.create_user(
            email="profile@example.com", password="ProfilePass!234"
        )

    def _auth(self):
        resp = self.client.post(
            "/api/users/login/",
            {"email": "profile@example.com", "password": "ProfilePass!234"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")

    def test_patch_updates_phone_bio_city_marketing(self):
        self._auth()
        resp = self.client.patch(
            "/api/users/me/",
            {
                "phone": "+380671112233",
                "bio": "Shawarma enthusiast.",
                "city": self.city.pk,
                "marketing_opt_in": True,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, "+380671112233")
        self.assertEqual(self.user.bio, "Shawarma enthusiast.")
        self.assertEqual(self.user.city_id, self.city.pk)
        self.assertTrue(self.user.marketing_opt_in)

    def test_patch_rejects_invalid_phone(self):
        self._auth()
        resp = self.client.patch("/api/users/me/", {"phone": "abc"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone", resp.data)

    def test_me_response_never_includes_password(self):
        self._auth()
        resp = self.client.get("/api/users/me/")
        self.assertNotIn("password", resp.data)


@override_settings(
    REST_FRAMEWORK={
        **NO_THROTTLE,
        **{
            "DEFAULT_AUTHENTICATION_CLASSES": [
                "rest_framework_simplejwt.authentication.JWTAuthentication",
            ],
            "DEFAULT_PERMISSION_CLASSES": [
                "rest_framework.permissions.IsAuthenticated",
            ],
            "DEFAULT_THROTTLE_CLASSES": [
                "rest_framework.throttling.ScopedRateThrottle",
            ],
        },
    }
)
class UserPublicProfileViewTests(APITestCase):
    """``GET /users/<id>/public/`` — safe profile view of another user."""

    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.city = City.objects.create(name="Test City", slug="test-city-odesa")
        self.user = User.objects.create_user(
            email="visible@example.com",
            password="VisiblePass!234",
            first_name="Vika",
            bio="I love shawarma.",
            phone="+380631112233",
            city=self.city,
        )
        self.banned = User.objects.create_user(
            email="banned@example.com", password="BannedPass!234", is_banned=True
        )
        self.inactive = User.objects.create_user(
            email="inactive@example.com", password="InactivePass!234", is_active=False
        )

    def test_anonymous_can_view_public_profile(self):
        resp = self.client.get(f"/api/users/{self.user.pk}/public/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["first_name"], "Vika")
        self.assertEqual(resp.data["city"]["slug"], "test-city-odesa")

    def test_public_profile_excludes_email_and_phone(self):
        resp = self.client.get(f"/api/users/{self.user.pk}/public/")
        self.assertNotIn("email", resp.data)
        self.assertNotIn("phone", resp.data)

    def test_banned_user_profile_is_not_found(self):
        resp = self.client.get(f"/api/users/{self.banned.pk}/public/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_inactive_user_profile_is_not_found(self):
        resp = self.client.get(f"/api/users/{self.inactive.pk}/public/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_unknown_user_profile_is_not_found(self):
        resp = self.client.get("/api/users/999999/public/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


@override_settings(
    REST_FRAMEWORK={
        **NO_THROTTLE,
        **{
            "DEFAULT_AUTHENTICATION_CLASSES": [
                "rest_framework_simplejwt.authentication.JWTAuthentication",
            ],
            "DEFAULT_PERMISSION_CLASSES": [
                "rest_framework.permissions.IsAuthenticated",
            ],
            "DEFAULT_THROTTLE_CLASSES": [
                "rest_framework.throttling.ScopedRateThrottle",
            ],
        },
    }
)
class AccountDeleteTests(APITestCase):
    """``POST /users/me/delete/`` — self-service account deletion."""

    delete_url = "/api/users/me/delete/"

    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.user = User.objects.create_user(
            email="leaving@example.com",
            password="LeavingPass!234",
            first_name="Leaving",
        )

    def _login(self):
        resp = self.client.post(
            "/api/users/login/",
            {"email": "leaving@example.com", "password": "LeavingPass!234"},
            format="json",
        )
        return resp.data["access"], resp.data["refresh"]

    def test_requires_authentication(self):
        resp = self.client.post(self.delete_url, {"password": "LeavingPass!234"})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rejects_wrong_password(self):
        access, _ = self._login()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        resp = self.client.post(self.delete_url, {"password": "WrongPass!234"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_deletes_and_anonymizes_account(self):
        access, refresh = self._login()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        resp = self.client.post(self.delete_url, {"password": "LeavingPass!234"})
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertNotEqual(self.user.email, "leaving@example.com")
        self.assertEqual(self.user.first_name, "")
        self.assertFalse(self.user.has_usable_password())

    def test_refresh_token_is_blacklisted_after_deletion(self):
        access, refresh = self._login()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        self.client.post(self.delete_url, {"password": "LeavingPass!234"})

        resp = self.client.post(
            "/api/users/token/refresh/", {"refresh": refresh}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deactivated_user_cannot_login(self):
        access, _ = self._login()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        self.client.post(self.delete_url, {"password": "LeavingPass!234"})

        resp = self.client.post(
            "/api/users/login/",
            {"email": "leaving@example.com", "password": "LeavingPass!234"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
