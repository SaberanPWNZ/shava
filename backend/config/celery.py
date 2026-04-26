"""Celery app for the Shava backend.

Loaded automatically by Django via :mod:`config.__init__`. Tasks are
auto-discovered from every Django app that exposes a ``tasks`` module
(e.g. :mod:`users.tasks`).

When ``REDIS_URL`` / ``CELERY_BROKER_URL`` are unset the app still
imports cleanly — :mod:`config.settings` flips
``CELERY_TASK_ALWAYS_EAGER`` on so callers using ``.delay()`` execute
synchronously inside the request thread. This keeps tests, CI and
single-machine dev running without a broker.
"""

from __future__ import annotations

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("shava")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
