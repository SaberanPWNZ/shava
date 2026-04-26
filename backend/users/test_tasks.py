"""Tests for the Celery wiring (ROADMAP 4.1).

Run in eager mode (``CELERY_TASK_ALWAYS_EAGER=True``) so we exercise
the task body without needing a broker. The eager-mode default is
flipped on automatically by ``config.settings`` whenever the test
suite is detected.
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings

from users.tasks import send_password_reset_email, send_verification_email

User = get_user_model()


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class CeleryEmailTaskTests(TestCase):
    """``.delay(user_id)`` dispatches and produces an outbox message."""

    def setUp(self):
        mail.outbox = []
        self.user = User.objects.create_user(
            username="celery-user",
            email="celery@example.com",
            password="StrongPass!234",
        )

    def test_send_verification_email_dispatched(self):
        send_verification_email.delay(self.user.pk).get(timeout=5)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user.email, mail.outbox[0].to)

    def test_send_password_reset_email_dispatched(self):
        send_password_reset_email.delay(self.user.pk).get(timeout=5)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user.email, mail.outbox[0].to)

    def test_task_drops_silently_when_user_is_missing(self):
        # Should not raise; nothing in the outbox.
        send_verification_email.delay(self.user.pk + 99999).get(timeout=5)
        self.assertEqual(len(mail.outbox), 0)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    REST_FRAMEWORK={
        "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "users.authentication.BanAwareJWTAuthentication"
        ],
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": 12,
        "DEFAULT_THROTTLE_CLASSES": [],
        "DEFAULT_THROTTLE_RATES": {},
    },
    AXES_ENABLED=False,
)
class RegistrationDispatchesViaCeleryTests(TestCase):
    """End-to-end: ``POST /api/v1/users/register/`` queues the task."""

    def setUp(self):
        mail.outbox = []

    def test_registration_enqueues_verification_email(self):
        from rest_framework.test import APIClient

        client = APIClient()
        resp = client.post(
            "/api/v1/users/register/",
            {
                "email": "newuser@example.com",
                "password": "StrongPass!234",
                "first_name": "N",
                "last_name": "U",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.content)
        # Eager mode runs the task inline, so the outbox is populated
        # by the time the response returns.
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("newuser@example.com", mail.outbox[0].to)
