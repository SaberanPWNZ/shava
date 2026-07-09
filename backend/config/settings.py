import os
import sys
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

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
        return "django-insecure-dev-only-do-not-use-in-production"
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY is required when DEBUG is False. "
        "Set it via environment variable / .env.prod."
    )


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
    "config.middleware.LegacyApiDeprecationMiddleware",
    "axes.middleware.AxesMiddleware",
]

API_LEGACY_SUNSET_DATE = (
    os.getenv("API_LEGACY_SUNSET_DATE", "Wed, 01 Oct 2026 00:00:00 GMT") or None
)

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AXES_ENABLED = _env_bool("AXES_ENABLED", default=not _RUNNING_TESTS)
AXES_FAILURE_LIMIT = int(os.getenv("AXES_FAILURE_LIMIT", "5"))
_axes_cooloff_hours = float(os.getenv("AXES_COOLOFF_TIME_HOURS", "1"))
AXES_COOLOFF_TIME = (
    timedelta(hours=_axes_cooloff_hours) if _axes_cooloff_hours > 0 else None
)
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_PARAMETERS = ["username", "ip_address"]
AXES_IPWARE_PROXY_COUNT = int(os.getenv("AXES_PROXY_COUNT", "1"))
AXES_LOCKOUT_TEMPLATE = None

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

CORS_ALLOWED_ORIGINS = _env_list(
    "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
)
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = _env_list("CSRF_TRUSTED_ORIGINS", "")

if not DEBUG and not _RUNNING_TESTS:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = _env_bool("SECURE_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE", True)
    CSRF_COOKIE_SECURE = _env_bool("CSRF_COOKIE_SECURE", True)
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = False
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

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")

EMAIL_VERIFY_TOKEN_MAX_AGE = int(os.getenv("EMAIL_VERIFY_TOKEN_MAX_AGE", "86400"))
PASSWORD_RESET_TOKEN_MAX_AGE = int(os.getenv("PASSWORD_RESET_TOKEN_MAX_AGE", "86400"))


STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


USE_S3_STORAGE = _env_bool("USE_S3_STORAGE", False)
if USE_S3_STORAGE:
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "").strip()
    if not AWS_STORAGE_BUCKET_NAME:
        raise ImproperlyConfigured(
            "USE_S3_STORAGE=True but AWS_STORAGE_BUCKET_NAME is empty."
        )
    _s3_options: dict[str, object] = {
        "bucket_name": AWS_STORAGE_BUCKET_NAME,
        "region_name": os.getenv("AWS_S3_REGION_NAME", "us-east-1"),
        "addressing_style": os.getenv("AWS_S3_ADDRESSING_STYLE", "path"),
        "querystring_auth": _env_bool("AWS_S3_QUERYSTRING_AUTH", default=False),
        "file_overwrite": _env_bool("AWS_S3_FILE_OVERWRITE", default=False),
        "use_ssl": _env_bool("AWS_S3_USE_SSL", default=True),
        "location": os.getenv("AWS_S3_LOCATION", ""),
    }
    _endpoint = os.getenv("AWS_S3_ENDPOINT_URL", "").strip()
    if _endpoint:
        _s3_options["endpoint_url"] = _endpoint
    _access = os.getenv("AWS_S3_ACCESS_KEY_ID", "").strip()
    _secret = os.getenv("AWS_S3_SECRET_ACCESS_KEY", "").strip()
    if _access and _secret:
        _s3_options["access_key"] = _access
        _s3_options["secret_key"] = _secret
    _custom_domain = os.getenv("AWS_S3_CUSTOM_DOMAIN", "").strip()
    if _custom_domain:
        _s3_options["custom_domain"] = _custom_domain
    _default_acl = os.getenv("AWS_S3_DEFAULT_ACL", "").strip()
    if _default_acl:
        _s3_options["default_acl"] = _default_acl

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": _s3_options,
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    _public_url = os.getenv("AWS_S3_PUBLIC_URL", "").strip()
    if _public_url:
        MEDIA_URL = _public_url.rstrip("/") + "/"


THUMBNAIL_ALIASES = {
    "avatar": {
        "xs": {"size": (64, 64), "crop": "smart", "quality": 80},
        "sm": {"size": (128, 128), "crop": "smart", "quality": 80},
        "md": {"size": (256, 256), "crop": "smart", "quality": 85},
        "lg": {"size": (512, 512), "crop": "smart", "quality": 85},
    },
    "photo": {
        "xs": {"size": (64, 0), "quality": 80},
        "sm": {"size": (256, 0), "quality": 80},
        "md": {"size": (512, 0), "quality": 85},
        "lg": {"size": (1024, 0), "quality": 85},
    },
}
THUMBNAIL_SRCSET_SIZES = (("xs", 64), ("sm", 256), ("md", 512), ("lg", 1024))
THUMBNAIL_DEBUG = False
THUMBNAIL_BASEDIR = "thumbs"


REDIS_URL = os.getenv("REDIS_URL", "").strip()
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "SOCKET_CONNECT_TIMEOUT": 5,
                "SOCKET_TIMEOUT": 5,
                "IGNORE_EXCEPTIONS": True,
            },
            "KEY_PREFIX": "shava",
        }
    }
    DJANGO_REDIS_IGNORE_EXCEPTIONS = True
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "shava-default",
        }
    }


CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "").strip() or REDIS_URL
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "").strip() or REDIS_URL
CELERY_TASK_ALWAYS_EAGER = (
    _env_bool("CELERY_TASK_ALWAYS_EAGER", default=not bool(CELERY_BROKER_URL))
    or _RUNNING_TESTS
)
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
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
            "maxBytes": 1024 * 1024 * 10,
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
            "maxBytes": 1024 * 1024 * 10,
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

# HttpOnly JWT cookies (see users/cookies.py). ``Secure`` outside DEBUG so
# tokens never travel over plain HTTP in production; ``Lax`` keeps them off
# cross-site POSTs (CSRF mitigation) while still working for the SPA.
JWT_COOKIE_SECURE = _env_bool("JWT_COOKIE_SECURE", default=not DEBUG)
JWT_COOKIE_SAMESITE = os.getenv("JWT_COOKIE_SAMESITE", "Lax")


INTERNAL_IPS = [
    "127.0.0.1",
]


from config.sentry import init_sentry

SENTRY_ENABLED = init_sentry()
