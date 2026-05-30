from django.urls import path

from apps.notifications.api.views import MarkNotificationReadView, NotificationListView

urlpatterns = [
    path("", NotificationListView.as_view(), name="api_notifications"),
    path(
        "<int:pk>/read/",
        MarkNotificationReadView.as_view(),
        name="api_mark_notification_read",
    ),
]
