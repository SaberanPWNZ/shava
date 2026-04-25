"""Django project package.

Importing :mod:`config.celery` here ensures the Celery app is registered
when Django starts so ``shared_task`` decorators in app modules bind to
the right Celery instance.
"""

from config.celery import app as celery_app

__all__ = ("celery_app",)
