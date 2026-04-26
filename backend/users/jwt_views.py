"""Throttled login view that uses email as the username field."""

from drf_spectacular.utils import extend_schema
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

from .jwt_serializers import EmailTokenObtainPairSerializer


@extend_schema(
    tags=["users"],
    summary="Obtain an access/refresh token pair (login)",
    description=(
        "Authenticate using ``email`` + ``password``. Returns a SimpleJWT "
        "access/refresh pair. Throttled under the ``auth`` scope and "
        "additionally rate-limited per IP/user by ``django-axes``."
    ),
)
class EmailTokenObtainPairView(TokenObtainPairView):
    """Login endpoint with rate-limiting (``auth`` scope)."""

    serializer_class = EmailTokenObtainPairSerializer  # type: ignore[assignment]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"
