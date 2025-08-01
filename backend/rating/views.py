from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Achievement, UserRating, UserAchievement
from .serializers import (
    AchievementSerializer,
    UserRatingSerializer,
    UserRatingCreateSerializer,
    UserAchievementSerializer
)


class AchievementViewSet(viewsets.ModelViewSet):
    """ViewSet for managing achievements."""
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """Only admins can create, update, or delete achievements."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class UserRatingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user ratings."""
    queryset = UserRating.objects.all()
    serializer_class = UserRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRatingCreateSerializer
        return UserRatingSerializer

    def get_permissions(self):
        """Only admins can create, update, or delete user ratings manually."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's rating profile."""
        try:
            user_rating = UserRating.objects.get(user=request.user)
            serializer = self.get_serializer(user_rating)
            return Response(serializer.data)
        except UserRating.DoesNotExist:
            return Response(
                {"detail": "User rating profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Get top users by experience points."""
        top_users = UserRating.objects.order_by('-experience_points')[:10]
        serializer = self.get_serializer(top_users, many=True)
        return Response(serializer.data)


class UserAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing user achievements."""
    queryset = UserAchievement.objects.all()
    serializer_class = UserAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter achievements by user if specified."""
        queryset = UserAchievement.objects.all()
        user_id = self.request.query_params.get('user', None)
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    @action(detail=False, methods=['get'])
    def my_achievements(self, request):
        """Get current user's achievements."""
        achievements = UserAchievement.objects.filter(user=request.user)
        serializer = self.get_serializer(achievements, many=True)
        return Response(serializer.data)
