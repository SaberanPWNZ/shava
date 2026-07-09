from django.urls import path

from notifications.views import MarkReadView, NotificationListView, UnreadCountView

urlpatterns = [
    path("", NotificationListView.as_view(), name="notifications-list"),
    path("unread-count/", UnreadCountView.as_view(), name="notifications-unread"),
    path("mark-read/", MarkReadView.as_view(), name="notifications-mark-read"),
]
