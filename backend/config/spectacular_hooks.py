"""drf-spectacular preprocessing hooks for the Shava schema.

Currently exposes :func:`only_versioned_paths`, which strips the legacy
unversioned ``/api/...`` mount from the emitted OpenAPI document. The
legacy paths still resolve at runtime (with a deprecation header) but
publishing both copies to the schema would double every operationId
and confuse generated clients.
"""

from __future__ import annotations

from collections.abc import Iterable


def only_versioned_paths(endpoints: Iterable[tuple], **_kwargs):
    """Drop endpoints that aren't under ``/api/v1/``.

    drf-spectacular calls this with a list of ``(path, path_regex,
    method, callback)`` tuples. We keep only the ones whose path starts
    with ``/api/v1/`` — every public route is dual-mounted, so the
    versioned variant is always present.
    """

    return [endpoint for endpoint in endpoints if endpoint[0].startswith("/api/v1/")]
