"""Regression tests for ``config.settings._resolve_secret_key``.

Roadmap 1.1 — Django must refuse to boot with an empty
``DJANGO_SECRET_KEY`` whenever ``DEBUG`` is off, so misconfigured
production deploys fail loudly at startup rather than silently shipping
with a blank key. The dev/test fallback must remain so the existing
``DJANGO_SECRET_KEY=test`` runner flow keeps working.
"""

from __future__ import annotations

import os
from unittest import TestCase, mock

from django.core.exceptions import ImproperlyConfigured

from config.settings import _resolve_secret_key


class ResolveSecretKeyTests(TestCase):
    def test_explicit_value_wins(self):
        with mock.patch.dict(os.environ, {"DJANGO_SECRET_KEY": "real-secret"}):
            self.assertEqual(
                _resolve_secret_key(debug=False, running_tests=False),
                "real-secret",
            )

    def test_empty_in_prod_raises_improperly_configured(self):
        with mock.patch.dict(os.environ, {"DJANGO_SECRET_KEY": ""}, clear=False):
            with self.assertRaises(ImproperlyConfigured):
                _resolve_secret_key(debug=False, running_tests=False)

    def test_unset_in_prod_raises_improperly_configured(self):
        env = {k: v for k, v in os.environ.items() if k != "DJANGO_SECRET_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ImproperlyConfigured):
                _resolve_secret_key(debug=False, running_tests=False)

    def test_empty_with_debug_uses_dev_fallback(self):
        with mock.patch.dict(os.environ, {"DJANGO_SECRET_KEY": ""}, clear=False):
            key = _resolve_secret_key(debug=True, running_tests=False)
        self.assertIn("insecure", key)

    def test_empty_with_test_runner_uses_dev_fallback(self):
        with mock.patch.dict(os.environ, {"DJANGO_SECRET_KEY": ""}, clear=False):
            key = _resolve_secret_key(debug=False, running_tests=True)
        self.assertIn("insecure", key)
