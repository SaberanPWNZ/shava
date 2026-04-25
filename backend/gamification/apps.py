from django.apps import AppConfig


class GamificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gamification"
    verbose_name = "Gamification"

    def ready(self):  # pragma: no cover - import side-effects only
        # Connect signal handlers so that domain events in `reviews`
        # automatically trigger points/badge awards. Importing here
        # avoids AppRegistryNotReady on startup.
        from . import signals  # noqa: F401
