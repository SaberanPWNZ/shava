import os
import sys
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv  # type: ignore

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _env_list(name: str, default: str = "") -> list[str]:
    return [v.strip() for v in os.getenv(name, default).split(",") if v.strip()]


def _resolve_secret_key(*, debug: bool, running_tests: bool) -> str:
    """Resolve ``SECRET_KEY`` from the environment with safe dev fallback.

    Raises :class:`~django.core.exceptions.ImproperlyConfigured` when
    ``DJANGO_SECRET_KEY`` is empty in a production-like context
    (``DEBUG=False`` and not a test run) so misconfigured deploys fail
    loudly at boot rather than silently shipping with a blank key.
    """

    key = os.getenv("DJANGO_SECRET_KEY", "")
    if key:
        return key
    if debug or running_tests:
        # Insecure fallback used only for local development / test runs.
        return "django-insecure-dev-only-do-not-use-in-production"
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY is required when DEBUG is False. "
        "Set it via environment variable / .env.prod."
    )


# Detect the test runner early so we don't enforce production-grade secrets in CI.
_RUNNING_TESTS = "test" in sys.argv

DEBUG = _env_bool("DEBUG", False)

SECRET_KEY = _resolve_secret_key(debug=DEBUG, running_tests=_RUNNING_TESTS)

ALLOWED_HOSTS = _env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")
SITE_ID = 1


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "news",
    "places",
    "users",
    "rating",
    "reviews",
    "shwarma",
    "ingredients",
    "places_menu",
    "articles",
    "gamification",
    "drf_spectacular",
    "axes",
    "easy_thumbnails",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Stamp Deprecation / Sunset / Link headers on legacy /api/ responses
    # so API consumers see the nudge to migrate to /api/v1/. Cheap, runs
    # last on the response so it sees the final status code regardless.
    "config.middleware.LegacyApiDeprecationMiddleware",
    # AxesMiddleware must be the *last* entry so that the request reaches
    # auth views first; it then increments the failure counter on
    # ``user_login_failed`` and serves a 403 Forbidden lockout response
    # once the configured threshold is exceeded.
    "axes.middleware.AxesMiddleware",
]

# Sunset date advertised on legacy /api/ responses (RFC 8594). Override via
# env if you want to push the deadline; ``None`` omits the header.
API_LEGACY_SUNSET_DATE = os.getenv(
    "API_LEGACY_SUNSET_DATE", "Wed, 01 Oct 2026 00:00:00 GMT"
) or None

# django-axes — brute-force protection. Layered on top of the existing DRF
# ScopedRateThrottle (which limits *rate*) by tracking *failures* per
# (username, ip) tuple. Disabled inside the test runner so unrelated tests
# don't hit the lockout state; enable explicitly with ``override_settings``
# in the dedicated lockout test.
AUTHENTICATION_BACKENDS = [
    # AxesStandaloneBackend must come before any other backend so it can
    # short-circuit authentication once the user is locked out.
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AXES_ENABLED = _env_bool("AXES_ENABLED", default=not _RUNNING_TESTS)
AXES_FAILURE_LIMIT = int(os.getenv("AXES_FAILURE_LIMIT", "5"))
# Cooloff window after which the lockout is automatically lifted. Express as
# a ``timedelta`` (django-axes also accepts plain hours, but the explicit
# type avoids any ambiguity for floats / sub-hour windows).
_axes_cooloff_hours = float(os.getenv("AXES_COOLOFF_TIME_HOURS", "1"))
AXES_COOLOFF_TIME = (
    timedelta(hours=_axes_cooloff_hours) if _axes_cooloff_hours > 0 else None
)
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_PARAMETERS = ["username", "ip_address"]
# Trust the standard X-Forwarded-For chain (single proxy = nginx).
AXES_IPWARE_PROXY_COUNT = int(os.getenv("AXES_PROXY_COUNT", "1"))
AXES_LOCKOUT_TEMPLATE = None  # JSON 403 from the API is fine.

# debug_toolbar is only enabled when DEBUG is True. It must never be active in
# production because it can leak settings, SQL, and request data.
if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

# CORS
CORS_ALLOWED_ORIGINS = _env_list(
    "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
)
CORS_ALLOW_CREDENTIALS = True

# CSRF trusted origins must include the scheme (https://...) and are required
# when serving the frontend from a different origin than the Django backend.
CSRF_TRUSTED_ORIGINS = _env_list("CSRF_TRUSTED_ORIGINS", "")

# ----- Production security hardening -----
# When DEBUG is False the app is assumed to run behind nginx terminating TLS.
# nginx passes the scheme via X-Forwarded-Proto so Django can correctly
# generate https URLs and enforce secure cookies.
if not DEBUG and not _RUNNING_TESTS:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = _env_bool("SECURE_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE", True)
    CSRF_COOKIE_SECURE = _env_bool("CSRF_COOKIE_SECURE", True)
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = False  # JS clients need to read the CSRF cookie.
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = _env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
    SECURE_HSTS_PRELOAD = _env_bool("SECURE_HSTS_PRELOAD", True)
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    X_FRAME_OPTIONS = "DENY"

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Use SQLite for testing
if _RUNNING_TESTS:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "shava_db"),
            "USER": os.getenv("POSTGRES_USER", "shava_user"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "shava_password"),
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# ----- Email -----------------------------------------------------------------
# Default to the console backend so local development and the initial VPS
# rollout don't need any SMTP credentials — verification / reset emails will
# print to stdout / container logs. Override via `EMAIL_BACKEND` env var (e.g.
# `django.core.mail.backends.smtp.EmailBackend` once an SMTP relay is wired).
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "25"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = _env_bool("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = _env_bool("EMAIL_USE_SSL", False)
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "10"))
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@shava.local")

# Single-domain deployment: the frontend (SvelteKit) is served from the same
# origin as the API in production. Verification / reset links embed this URL
# so we don't have to parse `Origin` headers and can build canonical links
# from CLI / Celery contexts as well.
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")

# Lifetimes (in seconds) for signed email tokens. Both default to 24h —
# long enough to survive a delayed inbox, short enough to limit replay risk.
EMAIL_VERIFY_TOKEN_MAX_AGE = int(os.getenv("EMAIL_VERIFY_TOKEN_MAX_AGE", "86400"))
PASSWORD_RESET_TOKEN_MAX_AGE = int(os.getenv("PASSWORD_RESET_TOKEN_MAX_AGE", "86400"))


STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ----- Image thumbnails (easy-thumbnails) ------------------------------------
# Aliases consumed by ``common.thumbnails.thumbnail_set`` so every API
# field exposing an image returns the same shape:
# ``{"src": original_url, "srcset": "...64w, ...256w, ...512w, ...1024w"}``.
# Using ``crop=smart`` for square avatars (so faces stay centred) and a
# plain scaled width for landscape-style place / article photos so we
# don't distort wide compositions.
THUMBNAIL_ALIASES = {
    # Square crops (avatars / small place tiles).
    "avatar": {
        "xs": {"size": (64, 64), "crop": "smart", "quality": 80},
        "sm": {"size": (128, 128), "crop": "smart", "quality": 80},
        "md": {"size": (256, 256), "crop": "smart", "quality": 85},
        "lg": {"size": (512, 512), "crop": "smart", "quality": 85},
    },
    # Landscape photos (place hero, review dish, article cover).
    "photo": {
        "xs": {"size": (64, 0), "quality": 80},
        "sm": {"size": (256, 0), "quality": 80},
        "md": {"size": (512, 0), "quality": 85},
        "lg": {"size": (1024, 0), "quality": 85},
    },
}
# Sizes for ``srcset`` width descriptors — keep in sync with the alias
# widths above. Stored as tuples of (alias, width-px).
THUMBNAIL_SRCSET_SIZES = (("xs", 64), ("sm", 256), ("md", 512), ("lg", 1024))
# Don't fail a request if a thumbnail can't be generated (corrupt source,
# missing file): emit ``None`` for that thumbnail and let the client fall
# back to the original ``src``.
THUMBNAIL_DEBUG = False
# Generate the file on demand the first time it's requested, then cache
# under ``MEDIA_ROOT/thumbs/`` exactly like the upload originals.
THUMBNAIL_BASEDIR = "thumbs"


# ----- Cache (django-redis when REDIS_URL is set) ----------------------------
REDIS_URL = os.getenv("REDIS_URL", "").strip()
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                # 5s connect / read timeouts so a flaky Redis can't pin
                # gunicorn workers indefinitely.
                "SOCKET_CONNECT_TIMEOUT": 5,
                "SOCKET_TIMEOUT": 5,
                "IGNORE_EXCEPTIONS": True,
            },
            "KEY_PREFIX": "shava",
        }
    }
    # If Redis is configured for cache, hand DRF rate-limiting the same
    # store so throttles work across gunicorn workers.
    DJANGO_REDIS_IGNORE_EXCEPTIONS = True
else:
    # In-process cache is fine for dev / tests / single-worker deploys.
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "shava-default",
        }
    }


# ----- Celery (async tasks) --------------------------------------------------
# Broker / result backend default to the same Redis URL — set
# CELERY_BROKER_URL explicitly only when you want to split brokers from
# the cache. When neither is configured we run ``ALWAYS_EAGER`` so calls
# to ``.delay()`` execute synchronously (dev, tests, CI).
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
# Eager when the broker is unset OR explicitly requested OR running tests.
CELERY_TASK_ALWAYS_EAGER = (
    _env_bool("CELERY_TASK_ALWAYS_EAGER", default=not bool(CELERY_BROKER_URL))
    or _RUNNING_TESTS
)
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
# Reasonable defaults — workers retry on broker connection loss but
# don't acknowledge until the task body has finished.
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1


REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "users.authentication.BanAwareJWTAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "auth": os.getenv("THROTTLE_AUTH", "5/min"),
        "register": os.getenv("THROTTLE_REGISTER", "10/hour"),
        "helpful": os.getenv("THROTTLE_HELPFUL", "30/min"),
        "email_verify": os.getenv("THROTTLE_EMAIL_VERIFY", "5/hour"),
        "password_reset": os.getenv("THROTTLE_PASSWORD_RESET", "5/hour"),
    },
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# ----- OpenAPI schema (drf-spectacular) --------------------------------------
# Exposed at /api/schema/, /api/docs/ (Swagger UI), /api/redoc/.
SPECTACULAR_SETTINGS = {
    "TITLE": "Shava API",
    "DESCRIPTION": (
        "Public REST API for the Shava project: places, reviews, ratings, "
        "users (JWT auth), articles, gamification."
    ),
    "VERSION": os.getenv("API_VERSION", "1.0.0"),
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": r"/api/v1/",
    # Drop the legacy unversioned ``/api/...`` mount from the emitted
    # schema — runtime keeps it as an alias with a deprecation header,
    # but generated clients should target ``/api/v1/`` only.
    "PREPROCESSING_HOOKS": ["config.spectacular_hooks.only_versioned_paths"],
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": False,
    },
}

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if not DEBUG else "DEBUG")
LOG_DIR = os.path.join(BASE_DIR, "logs")

if not os.path.exists("/.dockerenv"):
    os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} ({module}:{lineno}) — {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "json": {
            "format": '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s", "path": "%(pathname)s", "line": %(lineno)d}',
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose" if DEBUG else "simple",
            "level": LOG_LEVEL,
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": (
                os.path.join(LOG_DIR, "django.log")
                if not os.path.exists("/.dockerenv")
                else "/tmp/django.log"
            ),
            "formatter": "verbose",
            "level": LOG_LEVEL,
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": (
                os.path.join(LOG_DIR, "django_errors.log")
                if not os.path.exists("/.dockerenv")
                else "/tmp/django_errors.log"
            ),
            "formatter": "verbose",
            "level": "ERROR",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": (
                ["console", "error_file"]
                if not os.path.exists("/.dockerenv")
                else ["console"]
            ),
            "level": "WARNING",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "shava_project": {
            "handlers": (
                ["console", "file"]
                if not os.path.exists("/.dockerenv")
                else ["console"]
            ),
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "news": {
            "handlers": (
                ["console", "file"]
                if not os.path.exists("/.dockerenv")
                else ["console"]
            ),
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "places": {
            "handlers": (
                ["console", "file"]
                if not os.path.exists("/.dockerenv")
                else ["console"]
            ),
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "users": {
            "handlers": (
                ["console", "file"]
                if not os.path.exists("/.dockerenv")
                else ["console"]
            ),
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "rating": {
            "handlers": (
                ["console", "file"]
                if not os.path.exists("/.dockerenv")
                else ["console"]
            ),
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "reviews": {
            "handlers": (
                ["console", "file"]
                if not os.path.exists("/.dockerenv")
                else ["console"]
            ),
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "shwarma": {
            "handlers": (
                ["console", "file"]
                if not os.path.exists("/.dockerenv")
                else ["console"]
            ),
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "ingredients": {
            "handlers": (
                ["console", "file"]
                if not os.path.exists("/.dockerenv")
                else ["console"]
            ),
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
}

AUTH_USER_MODEL = "users.User"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
    "TOKEN_OBTAIN_SERIALIZER": "users.jwt_serializers.EmailTokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}


INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]


# ----- Sentry ----------------------------------------------------------------
# Initialised at the *very end* of settings so any prior import-time errors
# fail loudly during local development. When ``SENTRY_DSN`` is unset (the
# default for dev / test / CI) this call is a complete no-op.
from config.sentry import init_sentry  # noqa: E402

SENTRY_ENABLED = init_sentry()
