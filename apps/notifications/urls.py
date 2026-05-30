from django.urls import path

from . import views

urlpatterns = [
    # List all notifications for the logged-in user
    path("", views.notification_list, name="notification_list"),
    # Mark a single notification as read
    path("read/<int:notification_id>/", views.mark_as_read, name="mark_as_read"),
    # Mark all notifications as read
    path("read-all/", views.mark_all_read, name="mark_all_read"),
]
