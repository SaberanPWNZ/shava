from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenRefreshView

from users.jwt_views import EmailTokenObtainPairView

# All public REST endpoints live under a versioned prefix so we can roll
# out breaking changes without orphaning existing clients. The unversioned
# ``/api/`` paths are also kept for one release as an alias — responses
# carry a ``Deprecation`` / ``Sunset`` header (see
# ``config.middleware.LegacyApiDeprecationMiddleware``) so that consumers
# get a machine-readable nudge to switch to ``/api/v1/``.
api_v1_urlpatterns: list = [
    path("token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/", include("users.urls")),
    path("news/", include("news.urls")),
    path("places/", include("places.urls")),
    path("reviews/", include("reviews.urls")),
    path("articles/", include("articles.urls")),
    path("gamification/", include("gamification.urls")),
    # OpenAPI schema + UIs (drf-spectacular)
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_v1_urlpatterns)),
    # Legacy unversioned mount — kept for one release window. Same URL
    # pattern names as the v1 mount; ``reverse()`` resolves to the first
    # match (i.e. the v1 mount), which is what we want for templates and
    # schema URLs.
    path("api/", include(api_v1_urlpatterns)),
]

if settings.DEBUG:
    try:
        import debug_toolbar  # type: ignore

        urlpatterns += [
            path("__debug__/", include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass
