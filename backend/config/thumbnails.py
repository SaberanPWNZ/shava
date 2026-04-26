"""Helpers for exposing image thumbnails via the API.

Every endpoint that returns an image field also returns a sibling
``*_thumbnails`` field with the shape::

    {
        "src": "/media/place_images/x.jpg",
        "srcset": "/media/.../x.64x0.jpg 64w, ... 256w, ... 512w, ... 1024w",
        "sizes": {"xs": ".../x.64x0.jpg", "sm": ".../x.256x0.jpg", ...},
    }

The frontend can plug ``src`` + ``srcset`` straight into an ``<img>``
tag so browsers download the right size automatically. ``sizes`` is
exposed as a convenience for components that want to pick a specific
breakpoint without reparsing the ``srcset``.

Generation is delegated to ``easy-thumbnails``; aliases live in
``settings.THUMBNAIL_ALIASES`` and the alias widths are listed in
``settings.THUMBNAIL_SRCSET_SIZES``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.conf import settings
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.files import get_thumbnailer

if TYPE_CHECKING:
    from django.db.models.fields.files import ImageFieldFile

DEFAULT_ALIAS_GROUP = "photo"


def _absolute(url: str, request: Any | None) -> str:
    """Promote a relative ``/media/...`` URL to absolute when we have a request."""

    if request is None or url.startswith(("http://", "https://")):
        return url
    return request.build_absolute_uri(url)


def thumbnail_set(
    image: ImageFieldFile | None,
    *,
    alias_group: str = DEFAULT_ALIAS_GROUP,
    request: Any | None = None,
) -> dict[str, Any] | None:
    """Return the thumbnail bundle for ``image``.

    ``alias_group`` selects the set of aliases under
    ``settings.THUMBNAIL_ALIASES`` — typically ``"photo"`` (landscape)
    or ``"avatar"`` (square). Returns ``None`` when ``image`` is unset
    or its source file can't be opened (e.g. corrupt upload). The view
    layer then serialises the original URL with no thumbnails attached.
    """

    if not image or not getattr(image, "name", ""):
        return None

    aliases = settings.THUMBNAIL_ALIASES.get(alias_group)
    if not aliases:
        return None

    thumbnailer = get_thumbnailer(image)
    sizes: dict[str, str] = {}
    srcset_parts: list[str] = []

    for alias_name, _default_width in settings.THUMBNAIL_SRCSET_SIZES:
        options: dict[str, Any] | None = aliases.get(alias_name)
        if options is None:
            continue
        try:
            thumb = thumbnailer.get_thumbnail(options)
        except (InvalidImageFormatError, OSError, ValueError):
            # Bad / missing source — skip this width but keep going so
            # ``src`` + any successful thumbnails still serialise.
            continue
        url = _absolute(thumb.url, request)
        sizes[alias_name] = url
        # Use the actual generated width as the ``srcset`` descriptor.
        # ``options["size"]`` is ``(w, h)`` with one of the two
        # potentially zero (auto). Fall back to the alias's default
        # width when the helper can't read the value.
        size_tuple = options.get("size") or (_default_width, 0)
        width = size_tuple[0] or _default_width
        srcset_parts.append(f"{url} {width}w")

    return {
        "src": _absolute(image.url, request),
        "srcset": ", ".join(srcset_parts) if srcset_parts else None,
        "sizes": sizes,
    }
