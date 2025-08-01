from users.models import User
from rest_framework import viewsets, permissions, generics, status
from users.serializers import UserSerializer
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
    TokenAuthentication,
)
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()


class UserCreateViewSet(generics.CreateAPIView):
    """
    API endpoint that allows users to register without authentication.
    This endpoint is public and should NOT require any authentication.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get_permissions(self):
        logger.info("Getting permissions for UserCreateViewSet")
        return [permissions.AllowAny()]

    def create(self, request, *args, **kwargs):
        logger.info("Create method called in UserCreateViewSet")
        try:
            response = super().create(request, *args, **kwargs)
            logger.info(f"User creation successful: {response.data}")
            return response
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}", exc_info=True)
            return Response(
                {"detail": f"Failed to create user: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def dispatch(self, request, *args, **kwargs):
        logger.info(f"Request headers: {request.headers}")
        return super().dispatch(request, *args, **kwargs)


class UserDetailView(generics.RetrieveAPIView):
    """
    API endpoint that allows users to view their own profile.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
