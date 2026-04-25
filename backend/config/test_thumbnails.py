"""Tests for ``config.thumbnails.thumbnail_set`` (ROADMAP 4.3)."""

from __future__ import annotations

import io
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from config.thumbnails import thumbnail_set

User = get_user_model()


def _png_bytes(size: tuple[int, int] = (32, 32), colour: str = "red") -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color=colour).save(buf, format="PNG")
    return buf.getvalue()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix="shava-thumb-test-"))
class ThumbnailSetTests(TestCase):
    """The helper returns a stable shape with width-keyed sources."""

    def test_returns_none_for_empty_image(self):
        user = User.objects.create_user(
            username="noavatar", email="n@example.com", password="pw12345!"
        )
        # Force-clear the default avatar so we exercise the empty path.
        user.avatar = ""
        self.assertIsNone(thumbnail_set(user.avatar, alias_group="avatar"))

    def test_returns_set_for_uploaded_avatar(self):
        user = User.objects.create_user(
            username="hasavatar", email="h@example.com", password="pw12345!"
        )
        user.avatar.save(
            "h.png", SimpleUploadedFile("h.png", _png_bytes(), "image/png")
        )

        bundle = thumbnail_set(user.avatar, alias_group="avatar")
        self.assertIsNotNone(bundle)
        # Original URL is exposed under ``src``.
        self.assertEqual(bundle["src"], user.avatar.url)
        # All four configured aliases generated a sized variant.
        self.assertEqual(set(bundle["sizes"].keys()), {"xs", "sm", "md", "lg"})
        # ``srcset`` carries one descriptor per alias, with the actual
        # generated width.
        self.assertEqual(len(bundle["srcset"].split(",")), 4)
        for width in (64, 128, 256, 512):
            self.assertIn(f"{width}w", bundle["srcset"])

    def test_photo_alias_group_uses_landscape_widths(self):
        from places.models import Place

        place = Place.objects.create(
            name="P",
            city="Київ",
            address="x",
            main_image=SimpleUploadedFile(
                "p.png", _png_bytes(size=(800, 600)), "image/png"
            ),
            status="Active",
        )
        bundle = thumbnail_set(place.main_image, alias_group="photo")
        self.assertIsNotNone(bundle)
        for width in (64, 256, 512, 1024):
            self.assertIn(f"{width}w", bundle["srcset"])

    def test_unknown_alias_group_returns_none(self):
        user = User.objects.create_user(
            username="x", email="x@example.com", password="pw12345!"
        )
        user.avatar.save(
            "x.png", SimpleUploadedFile("x.png", _png_bytes(), "image/png")
        )
        self.assertIsNone(thumbnail_set(user.avatar, alias_group="does-not-exist"))
