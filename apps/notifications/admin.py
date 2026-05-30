from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for easy inspection of notifications.
    """

    list_display = ("title", "user", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("title", "message", "user__username")
    readonly_fields = ("created_at",)
    list_per_page = 25
