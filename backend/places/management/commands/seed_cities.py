"""Seed the :class:`places.City` table from a CSV file.

Usage::

    python manage.py seed_cities
    python manage.py seed_cities --file path/to/cities.csv

The CSV must have a header row with at least ``name`` and ``slug`` columns;
``region`` is optional. Existing rows (matched by slug) are updated in place,
so the command is idempotent.
"""

from __future__ import annotations

import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from places.models import City

DEFAULT_CSV = Path(__file__).resolve().parent.parent.parent / "data" / "cities.csv"


class Command(BaseCommand):
    help = "Seed the places.City table from a CSV file (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            "-f",
            type=str,
            default=str(DEFAULT_CSV),
            help="Path to the cities CSV. Defaults to backend/places/data/cities.csv.",
        )
        parser.add_argument(
            "--deactivate-missing",
            action="store_true",
            help=(
                "Mark cities not present in the CSV as inactive instead of "
                "leaving them untouched."
            ),
        )

    def handle(self, *args, **options):
        path = Path(options["file"])
        if not path.is_file():
            raise CommandError(f"CSV file not found: {path}")

        with path.open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            missing = {
                col for col in ("name", "slug") if col not in (reader.fieldnames or [])
            }
            if missing:
                raise CommandError(
                    f"CSV is missing required columns: {', '.join(sorted(missing))}"
                )
            seen_slugs: set[str] = set()
            created = updated = 0
            for row in reader:
                name = (row.get("name") or "").strip()
                slug = (row.get("slug") or "").strip()
                region = (row.get("region") or "").strip()
                if not name or not slug:
                    continue
                seen_slugs.add(slug)
                _, was_created = City.objects.update_or_create(
                    slug=slug,
                    defaults={"name": name, "region": region, "is_active": True},
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

        deactivated = 0
        if options["deactivate_missing"] and seen_slugs:
            deactivated = City.objects.exclude(slug__in=seen_slugs).update(
                is_active=False
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed cities done: created={created}, updated={updated}, "
                f"deactivated={deactivated} (source={path})."
            )
        )
