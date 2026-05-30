from django.conf import settings
from django.db import models

from apps.notifications.constants import NotificationType


class Notification(models.Model):
    """
    Stores in-app notifications for users.
    Each notification can optionally link back to the FoodPost that triggered it.
    """

    Type = NotificationType

    # Who receives this notification
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="The user who will see this notification.",
        db_index=True,
    )

    # Type of notification (for filtering and icon display)
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        help_text="Category of the notification event.",
        db_index=True,
    )

    title = models.CharField(max_length=200, help_text="Short headline.")
    message = models.TextField(help_text="Detailed notification text.")

    # Optional link back to the food post that caused this notification
    related_food_post = models.ForeignKey(
        "food.FoodPost",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
        help_text="The food post related to this notification, if any.",
        db_index=True,
    )

    is_read = models.BooleanField(
        default=False,
        help_text="Whether the user has read this notification.",
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]  # Newest first
        indexes = [
            # Speed up queries for unread notifications per user
            models.Index(fields=["user", "is_read"]),
        ]

    def __str__(self):
        status = "Read" if self.is_read else "Unread"
        return f"[{status}] {self.title} → {self.user.username}"
