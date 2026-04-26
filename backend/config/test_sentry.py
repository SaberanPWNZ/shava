"""Tests for the Sentry initialisation helper.

We never want test runs to emit events to a real Sentry instance, so the
test suite asserts:

1. With no ``SENTRY_DSN`` set, ``init_sentry()`` returns ``False`` and the
   SDK's hub stays uninitialised.
2. With a fake DSN set, ``init_sentry()`` returns ``True`` and ``sentry_sdk``
   is configured with ``send_default_pii=False`` and the release / env we
   passed in.
"""

from __future__ import annotations

import os
import unittest
from unittest import mock

from config.sentry import init_sentry


class SentryInitTests(unittest.TestCase):
    def setUp(self) -> None:
        # Snapshot env so tests don't leak state into one another.
        self._snapshot = {
            k: os.environ.get(k)
            for k in (
                "SENTRY_DSN",
                "SENTRY_RELEASE",
                "GIT_SHA",
                "SENTRY_ENVIRONMENT",
                "SENTRY_TRACES_SAMPLE_RATE",
            )
        }
        for k in self._snapshot:
            os.environ.pop(k, None)

    def tearDown(self) -> None:
        for k, v in self._snapshot.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_init_is_noop_without_dsn(self):
        with mock.patch("sentry_sdk.init") as init:
            self.assertFalse(init_sentry())
            init.assert_not_called()

    def test_init_passes_pii_off_and_release(self):
        os.environ["SENTRY_DSN"] = "https://public@example.ingest.sentry.io/1"
        os.environ["GIT_SHA"] = "abc1234"
        os.environ["SENTRY_ENVIRONMENT"] = "test-prod"
        os.environ["SENTRY_TRACES_SAMPLE_RATE"] = "0.25"

        with mock.patch("sentry_sdk.init") as init:
            self.assertTrue(init_sentry())
            init.assert_called_once()
            kwargs = init.call_args.kwargs
            self.assertFalse(kwargs["send_default_pii"])
            self.assertEqual(kwargs["release"], "abc1234")
            self.assertEqual(kwargs["environment"], "test-prod")
            self.assertEqual(kwargs["traces_sample_rate"], 0.25)
            # Default profiles sample rate stays 0 unless explicitly opted in.
            self.assertEqual(kwargs["profiles_sample_rate"], 0.0)

    def test_invalid_traces_sample_rate_falls_back_to_default(self):
        os.environ["SENTRY_DSN"] = "https://public@example.ingest.sentry.io/1"
        os.environ["SENTRY_TRACES_SAMPLE_RATE"] = "not-a-number"
        with mock.patch("sentry_sdk.init") as init:
            self.assertTrue(init_sentry())
            self.assertEqual(init.call_args.kwargs["traces_sample_rate"], 0.0)
