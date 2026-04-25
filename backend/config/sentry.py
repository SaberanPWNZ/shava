"""Sentry initialisation, isolated from ``settings`` so it can be tested.

Initialises the Sentry SDK exactly once per process — and **only** when a
``SENTRY_DSN`` is configured. This means:

* Local development (no DSN) → no network traffic, no overhead.
* CI / unit tests (no DSN) → no events emitted, deterministic test runs.
* Production (DSN set in ``.env.prod``) → reports unhandled exceptions.

PII is off by default (``send_default_pii=False``); only the user id is
attached automatically by the Django integration when a request is
authenticated.
"""

from __future__ import annotations

import os


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def init_sentry() -> bool:
    """Initialise Sentry if ``SENTRY_DSN`` is set. Returns ``True`` on init.

    Safe to import / call at any time — when Sentry is not configured this
    function is a no-op and never imports the SDK.
    """
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return False

    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
    except ImportError:
        # The dependency is part of ``requirements.txt``; if it's missing
        # in some constrained environment we degrade gracefully rather
        # than blow up the whole settings import.
        return False

    sentry_sdk.init(
        dsn=dsn,
        environment=os.getenv("SENTRY_ENVIRONMENT", os.getenv("DJANGO_ENV", "production")),
        release=os.getenv("SENTRY_RELEASE") or os.getenv("GIT_SHA") or None,
        integrations=[
            DjangoIntegration(),
            # ERROR-and-above are sent as events; INFO+ becomes breadcrumbs.
            LoggingIntegration(level=None, event_level=None),
        ],
        # Performance / profiling — opt-in via env, default off so the free
        # tier of Sentry isn't burnt through by accident.
        traces_sample_rate=_env_float("SENTRY_TRACES_SAMPLE_RATE", 0.0),
        profiles_sample_rate=_env_float("SENTRY_PROFILES_SAMPLE_RATE", 0.0),
        # Privacy: never attach IPs, cookies, or request bodies by default.
        send_default_pii=False,
    )
    return True


__all__ = ["init_sentry"]
