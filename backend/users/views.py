from users.models import User
from rest_framework import viewsets, permissions, generics
from users.serializers import UserSerializer


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
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        print("UserCreateViewSet permissions:", self.permission_classes)
        return [permission() for permission in self.permission_classes]
