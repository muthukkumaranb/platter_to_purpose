from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

from apps.notifications.selectors import get_unread_count, get_user_notifications
from apps.notifications.services import (
    mark_all_notifications_as_read,
    mark_notification_as_read,
)


@login_required
def notification_list(request):
    notifications = get_user_notifications(request.user)
    unread_count = get_unread_count(request.user)

    return render(
        request,
        "notifications/notification_list.html",
        {
            "notifications": notifications,
            "unread_count": unread_count,
        },
    )


@login_required
def mark_as_read(request, notification_id):
    mark_notification_as_read(request.user, notification_id)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        unread_count = get_unread_count(request.user)
        return JsonResponse({"status": "ok", "unread_count": unread_count})

    return redirect("notification_list")


@login_required
def mark_all_read(request):
    mark_all_notifications_as_read(request.user)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"status": "ok", "unread_count": 0})

    return redirect("notification_list")
