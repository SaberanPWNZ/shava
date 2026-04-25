"""Tests for the email-driven flows: verification + password reset."""

from __future__ import annotations

import time
from unittest.mock import patch

from django.core import mail
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from users.tokens import (
    TokenInvalid,
    make_password_reset_token,
    make_verify_email_token,
    read_password_reset_token,
    read_verify_email_token,
)

# Match the pattern used by the existing AuthFlowTests: disable throttling
# and JWT-only auth so token-flow tests don't get rate-limited or hit the
# axes lockout layer.
NO_THROTTLE = {
    "DEFAULT_THROTTLE_RATES": {
        "auth": "1000/min",
        "register": "1000/min",
        "email_verify": "1000/min",
        "password_reset": "1000/min",
    },
}

OVERRIDE_REST = {
    **NO_THROTTLE,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
    ],
}


@override_settings(
    REST_FRAMEWORK=OVERRIDE_REST,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    FRONTEND_URL="http://testserver-frontend",
)
class VerifyEmailFlowTests(APITestCase):
    register_url = "/api/users/register/"
    login_url = "/api/users/login/"
    request_url = "/api/users/verify-email/request/"
    confirm_url = "/api/users/verify-email/confirm/"

    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        mail.outbox = []

    def _register(self, email="alice@example.com"):
        response = self.client.post(
            self.register_url,
            {"email": email, "password": "StrongPass!234", "first_name": "Alice"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return User.objects.get(email=email)

    def _login(self, email="alice@example.com", password="StrongPass!234"):
        return self.client.post(
            self.login_url, {"email": email, "password": password}, format="json"
        )

    # --- Registration sends a verification email ---------------------------

    def test_registration_sends_verification_email(self):
        self._register()
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertIn("alice@example.com", msg.to)
        # Frontend URL embedded.
        self.assertIn("http://testserver-frontend/verify-email/", msg.body)
        # UA template uses Cyrillic "Підтвердження".
        self.assertIn("Підтвердження", msg.subject)

    # --- Confirm: happy path ----------------------------------------------

    def test_confirm_marks_user_verified(self):
        user = self._register()
        self.assertFalse(user.is_verified)
        token = make_verify_email_token(user)

        response = self.client.post(
            self.confirm_url, {"token": token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_verified)
        self.assertTrue(response.data["is_verified"])

    # --- Confirm: replay (already-verified token) -------------------------

    def test_confirm_token_cannot_be_replayed_after_verification(self):
        user = self._register()
        token = make_verify_email_token(user)
        self.client.post(self.confirm_url, {"token": token}, format="json")

        # Second use should be rejected — the token's fingerprint no longer
        # matches the user's current ``is_verified`` state.
        response = self.client.post(
            self.confirm_url, {"token": token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Confirm: tampered / unknown / expired ----------------------------

    def test_confirm_rejects_tampered_token(self):
        user = self._register()
        token = make_verify_email_token(user) + "garbage"
        response = self.client.post(
            self.confirm_url, {"token": token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_rejects_wrong_purpose_token(self):
        """A password-reset token must not be accepted by verify-email."""
        user = self._register()
        token = make_password_reset_token(user)
        response = self.client.post(
            self.confirm_url, {"token": token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(EMAIL_VERIFY_TOKEN_MAX_AGE=1)
    def test_confirm_rejects_expired_token(self):
        user = self._register()
        token = make_verify_email_token(user)
        time.sleep(1.1)
        response = self.client.post(
            self.confirm_url, {"token": token}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Re-send (request) endpoint ---------------------------------------

    def test_request_sends_email_for_authenticated_unverified_user(self):
        self._register()
        access = self._login().data["access"]
        mail.outbox = []
        response = self.client.post(
            self.request_url,
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(mail.outbox), 1)

    def test_request_is_noop_for_already_verified_user(self):
        user = self._register()
        user.is_verified = True
        user.save(update_fields=["is_verified"])
        access = self._login().data["access"]
        mail.outbox = []
        response = self.client.post(
            self.request_url,
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(mail.outbox), 0)

    def test_request_rejects_anonymous(self):
        response = self.client.post(self.request_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@override_settings(
    REST_FRAMEWORK=OVERRIDE_REST,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    FRONTEND_URL="http://testserver-frontend",
)
class PasswordResetFlowTests(APITestCase):
    register_url = "/api/users/register/"
    login_url = "/api/users/login/"
    request_url = "/api/users/password-reset/request/"
    confirm_url = "/api/users/password-reset/confirm/"

    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        mail.outbox = []

    def _register(self, email="bob@example.com"):
        self.client.post(
            self.register_url,
            {"email": email, "password": "StrongPass!234", "first_name": "Bob"},
            format="json",
        )
        return User.objects.get(email=email)

    # --- Request endpoint: enumeration-safe -------------------------------

    def test_request_for_known_user_sends_email(self):
        self._register()
        mail.outbox = []
        response = self.client.post(
            self.request_url, {"email": "bob@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(
            "http://testserver-frontend/reset-password/", mail.outbox[0].body
        )
        # UA subject.
        self.assertIn("Скидання", mail.outbox[0].subject)

    def test_request_for_unknown_user_does_not_leak(self):
        response = self.client.post(
            self.request_url, {"email": "nobody@example.com"}, format="json"
        )
        # Same response shape, no email queued.
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(mail.outbox), 0)

    def test_request_swallows_transport_errors(self):
        """A failing SMTP relay must not turn the endpoint into an oracle."""
        self._register()
        mail.outbox = []
        with patch(
            "users.views.PasswordResetRequestView.email_service."
            "send_password_reset_email",
            side_effect=RuntimeError("smtp down"),
        ):
            response = self.client.post(
                self.request_url, {"email": "bob@example.com"}, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # --- Confirm: happy path ----------------------------------------------

    def test_confirm_resets_password(self):
        user = self._register()
        token = make_password_reset_token(user)
        response = self.client.post(
            self.confirm_url,
            {"token": token, "new_password": "BrandNewPass!234"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user.refresh_from_db()
        self.assertTrue(user.check_password("BrandNewPass!234"))

    # --- Confirm: replay -------------------------------------------------

    def test_confirm_token_cannot_be_replayed(self):
        user = self._register()
        token = make_password_reset_token(user)
        self.client.post(
            self.confirm_url,
            {"token": token, "new_password": "BrandNewPass!234"},
            format="json",
        )
        # Second use must fail because the password has changed.
        response = self.client.post(
            self.confirm_url,
            {"token": token, "new_password": "AnotherPass!234"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Confirm: tampered / wrong purpose / expired ---------------------

    def test_confirm_rejects_tampered_token(self):
        user = self._register()
        token = make_password_reset_token(user) + "garbage"
        response = self.client.post(
            self.confirm_url,
            {"token": token, "new_password": "BrandNewPass!234"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_rejects_wrong_purpose_token(self):
        user = self._register()
        token = make_verify_email_token(user)
        response = self.client.post(
            self.confirm_url,
            {"token": token, "new_password": "BrandNewPass!234"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(PASSWORD_RESET_TOKEN_MAX_AGE=1)
    def test_confirm_rejects_expired_token(self):
        user = self._register()
        token = make_password_reset_token(user)
        time.sleep(1.1)
        response = self.client.post(
            self.confirm_url,
            {"token": token, "new_password": "BrandNewPass!234"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_rejects_weak_password(self):
        user = self._register()
        token = make_password_reset_token(user)
        response = self.client.post(
            self.confirm_url,
            {"token": token, "new_password": "123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)


class TokenUtilsTests(APITestCase):
    """Direct unit tests for users.tokens — independent of HTTP wiring."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="charlie@example.com", password="StrongPass!234"
        )

    def test_verify_token_round_trip(self):
        token = make_verify_email_token(self.user)
        result = read_verify_email_token(token)
        self.assertEqual(result.pk, self.user.pk)

    def test_verify_token_invalidated_after_state_change(self):
        token = make_verify_email_token(self.user)
        self.user.is_verified = True
        self.user.save(update_fields=["is_verified"])
        with self.assertRaises(TokenInvalid):
            read_verify_email_token(token)

    def test_password_reset_token_invalidated_after_password_change(self):
        token = make_password_reset_token(self.user)
        self.user.set_password("DifferentPass!234")
        self.user.save(update_fields=["password"])
        with self.assertRaises(TokenInvalid):
            read_password_reset_token(token)

    def test_cross_purpose_token_rejected(self):
        verify_token = make_verify_email_token(self.user)
        with self.assertRaises(TokenInvalid):
            read_password_reset_token(verify_token)
