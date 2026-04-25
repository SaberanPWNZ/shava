"""Seed the City catalogue from the bundled CSV and backfill Place.city_ref.

Idempotent: existing City rows (matched by slug) are updated in place, and
Place rows whose ``city`` text matches a known city name are linked.
"""

from __future__ import annotations

import csv
from pathlib import Path

from django.db import migrations


CITIES_CSV = (
    Path(__file__).resolve().parent.parent / "data" / "cities.csv"
)


def _read_cities() -> list[dict[str, str]]:
    if not CITIES_CSV.is_file():
        return []
    with CITIES_CSV.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        rows: list[dict[str, str]] = []
        for row in reader:
            name = (row.get("name") or "").strip()
            slug = (row.get("slug") or "").strip()
            if not name or not slug:
                continue
            rows.append(
                {
                    "name": name,
                    "slug": slug,
                    "region": (row.get("region") or "").strip(),
                }
            )
        return rows


def seed_and_backfill(apps, schema_editor):
    City = apps.get_model("places", "City")
    Place = apps.get_model("places", "Place")

    rows = _read_cities()
    name_to_id: dict[str, int] = {}
    for row in rows:
        obj, _ = City.objects.update_or_create(
            slug=row["slug"],
            defaults={
                "name": row["name"],
                "region": row["region"],
                "is_active": True,
            },
        )
        name_to_id[row["name"].lower()] = obj.id

    if not name_to_id:
        return
    # Backfill the FK on existing places whose free-text city matches a row
    # in the catalogue (case-insensitive). Anything else is left as NULL.
    for place in Place.objects.filter(city_ref__isnull=True).iterator():
        key = (place.city or "").strip().lower()
        cid = name_to_id.get(key)
        if cid is not None:
            Place.objects.filter(pk=place.pk).update(city_ref_id=cid)


def unseed(apps, schema_editor):
    # Reverse migration: drop the FK pointers but keep the City rows in case
    # the operator wants to roll the schema migration back without losing
    # reference data they may have edited via admin.
    Place = apps.get_model("places", "Place")
    Place.objects.filter(city_ref__isnull=False).update(city_ref=None)


class Migration(migrations.Migration):

    dependencies = [
        ("places", "0006_city_place_city_ref"),
    ]

    operations = [
        migrations.RunPython(seed_and_backfill, unseed),
    ]
