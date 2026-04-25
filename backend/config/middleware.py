"""Project-level Django middleware.

Currently exposes :class:`LegacyApiDeprecationMiddleware`, which stamps
``Deprecation`` / ``Sunset`` / ``Link`` headers on every response served
under the legacy unversioned ``/api/`` prefix so that API consumers get
a machine-readable signal to migrate to ``/api/v1/``.

The headers are modelled after IETF drafts widely supported by API
gateway tooling:

* ``Deprecation: true`` — RFC 9745 (formerly draft-ietf-httpapi-deprecation).
* ``Sunset: <HTTP-date>`` — RFC 8594. The date is configured via the
  ``API_LEGACY_SUNSET_DATE`` setting and defaults to roughly one release
  window from now.
* ``Link: </api/v1/...>; rel="successor-version"`` — RFC 8631.

We intentionally do **not** issue a 308 redirect: SPA POSTs would have
to follow it, the existing `/api/` URLs already work on every method,
and a soft header-based deprecation is what every major API (Stripe,
GitHub, Twilio) uses for this pattern. See ``ROADMAP.md`` 3.2.
"""

from __future__ import annotations

from collections.abc import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse


class LegacyApiDeprecationMiddleware:
    """Annotate responses for legacy ``/api/...`` (non-versioned) routes."""

    LEGACY_PREFIX = "/api/"
    VERSIONED_PREFIX = "/api/v1/"

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response
        self.sunset_date: str | None = getattr(
            settings, "API_LEGACY_SUNSET_DATE", None
        )

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        path = request.path
        if path.startswith(self.LEGACY_PREFIX) and not path.startswith(
            self.VERSIONED_PREFIX
        ):
            # Per RFC 9745 the value is a structured-fields boolean.
            response["Deprecation"] = "true"
            if self.sunset_date:
                response["Sunset"] = self.sunset_date
            successor = self.VERSIONED_PREFIX + path[len(self.LEGACY_PREFIX):]
            response["Link"] = f'<{successor}>; rel="successor-version"'
        return response
