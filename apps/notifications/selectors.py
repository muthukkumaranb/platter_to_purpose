from django.db.models import QuerySet

from apps.notifications.models import Notification


def get_user_notifications(user) -> QuerySet[Notification]:
    """
    Retrieves all notifications for a user.
    """
    return Notification.objects.filter(user=user)


def get_unread_count(user) -> int:
    """
    Gets the count of unread notifications for a user.
    """
    return Notification.objects.filter(user=user, is_read=False).count()
