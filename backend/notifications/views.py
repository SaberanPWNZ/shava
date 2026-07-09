from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers as drf_serializers
from rest_framework import views
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications.models import Notification
from notifications.serializers import NotificationSerializer


@extend_schema(tags=["notifications"], summary="List the viewer's notifications")
class NotificationListView(ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@extend_schema(tags=["notifications"])
class UnreadCountView(views.APIView):
    """Cheap endpoint the header bell polls on page load."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Number of unread notifications",
        responses={
            200: inline_serializer(
                name="UnreadCountResponse",
                fields={"unread": drf_serializers.IntegerField()},
            )
        },
    )
    def get(self, request):
        unread = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread": unread})


@extend_schema(tags=["notifications"])
class MarkReadView(views.APIView):
    """Mark specific notifications (``{"ids": [...]}``) or all of them
    (empty body / ``{"all": true}``) as read."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Mark notifications as read",
        request=inline_serializer(
            name="MarkReadRequest",
            fields={
                "ids": drf_serializers.ListField(
                    child=drf_serializers.IntegerField(), required=False
                ),
            },
        ),
        responses={
            200: inline_serializer(
                name="MarkReadResponse",
                fields={"marked": drf_serializers.IntegerField()},
            )
        },
    )
    def post(self, request):
        qs = Notification.objects.filter(user=request.user, is_read=False)
        ids = request.data.get("ids")
        if ids is not None:
            if not isinstance(ids, list) or not all(isinstance(pk, int) for pk in ids):
                return Response({"ids": ["Must be a list of integers."]}, status=400)
            qs = qs.filter(id__in=ids)
        marked = qs.update(is_read=True)
        return Response({"marked": marked})
