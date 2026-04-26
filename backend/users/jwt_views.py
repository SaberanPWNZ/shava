"""Throttled login view that uses email as the username field."""

from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

from .jwt_serializers import EmailTokenObtainPairSerializer


class EmailTokenObtainPairView(TokenObtainPairView):
    """Login endpoint with rate-limiting (``auth`` scope)."""

    serializer_class = EmailTokenObtainPairSerializer  # type: ignore[assignment]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"
