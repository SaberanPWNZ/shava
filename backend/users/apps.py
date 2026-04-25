from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    def ready(self) -> None:
        # Register the drf-spectacular authentication extension for
        # BanAwareJWTAuthentication so every endpoint resolves to the
        # standard bearerAuth scheme instead of emitting a warning.
        from . import schema  # noqa: F401
