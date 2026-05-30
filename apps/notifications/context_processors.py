from .models import Notification


def unread_notifications(request):
    """
    Template context processor that injects the unread notification count
    into every template. This powers the badge number on the navbar bell icon.

    For anonymous users (not logged in), returns 0.
    """
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {"unread_notification_count": count}
    return {"unread_notification_count": 0}
