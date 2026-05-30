from django.shortcuts import get_object_or_404

from apps.notifications.models import Notification


def send_notification(user, event_type, payload) -> Notification:
    """
    Creates and saves a notification record for a user.
    """
    notification = Notification.objects.create(
        user=user,
        notification_type=event_type,
        title=payload.get("title", ""),
        message=payload.get("message", ""),
        related_food_post=payload.get("related_food_post"),
    )
    return notification


def mark_notification_as_read(user, notification_id) -> Notification:
    """
    Marks a single notification as read.
    """
    notification = get_object_or_404(Notification, pk=notification_id, user=user)
    notification.is_read = True
    notification.save()
    return notification


def mark_all_notifications_as_read(user):
    """
    Marks all unread notifications for a user as read.
    """
    Notification.objects.filter(user=user, is_read=False).update(is_read=True)
