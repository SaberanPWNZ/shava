import os
import sys
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv  # type: ignore

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _env_list(name: str, default: str = "") -> list[str]:
    return [v.strip() for v in os.getenv(name, default).split(",") if v.strip()]


# Detect the test runner early so we don't enforce production-grade secrets in CI.
_RUNNING_TESTS = "test" in sys.argv

DEBUG = _env_bool("DEBUG", False)

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG or _RUNNING_TESTS:
        # Insecure fallback used only for local development / test runs.
        SECRET_KEY = "django-insecure-dev-only-do-not-use-in-production"
    else:
        raise RuntimeError(
            "DJANGO_SECRET_KEY is required when DEBUG is False. "
            "Set it via environment variable / .env.prod."
        )

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
    # AxesMiddleware must be the *last* entry so that the request reaches
    # auth views first; it then increments the failure counter on
    # ``user_login_failed`` and serves a 429-equivalent lockout response
    # once the configured threshold is exceeded.
    "axes.middleware.AxesMiddleware",
]

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
AXES_COOLOFF_TIME = timedelta(hours=_axes_cooloff_hours) if _axes_cooloff_hours > 0 else None
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
    SECURE_HSTS_INCLUDE_SUBDOMAINS = _env_bool(
        "SECURE_HSTS_INCLUDE_SUBDOMAINS", True
    )
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
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
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


STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


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
    "SCHEMA_PATH_PREFIX": r"/api/",
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
