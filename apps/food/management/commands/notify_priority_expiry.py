"""
food/management/commands/notify_priority_expiry.py
──────────────────────────────────────────────────
Run via cron every 5 minutes:
    */5 * * * * python manage.py notify_priority_expiry

Finds food posts whose priority window just expired (within the last
5 minutes) that are STILL unclaimed, and notifies all Hotels.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.food.models import FoodPost
from apps.notifications.models import Notification


class Command(BaseCommand):
    help = "Notify hotels about food posts whose priority window just expired."

    def handle(self, *args, **options):
        now = timezone.now()
        # Look back 5 minutes to catch windows that expired since last run
        lookback = now - timedelta(minutes=5)

        # Find posts where:
        # 1. Priority window ended between lookback and now
        # 2. Still unclaimed
        # 3. Not yet expired (expiry_time > now)
        expired_window_posts = FoodPost.objects.filter(
            priority_window_ends__gt=lookback,
            priority_window_ends__lte=now,
            is_claimed=False,
            expiry_time__gt=now,
        )

        if not expired_window_posts.exists():
            self.stdout.write(self.style.SUCCESS("No newly expired priority windows."))
            return

        # Get all hotel users
        from django.contrib.auth import get_user_model

        User = get_user_model()  # noqa: N806
        hotels = User.objects.filter(role="HOTEL")

        if not hotels.exists():
            self.stdout.write(self.style.WARNING("No hotel users found."))
            return

        notifications = []
        for food in expired_window_posts:
            for hotel in hotels:
                # Don't notify the donor about their own post
                if hotel == food.donor:
                    continue

                expiry_str = (
                    food.expiry_time.strftime("%b %d, %I:%M %p")
                    if food.expiry_time
                    else "N/A"
                )
                notifications.append(
                    Notification(
                        user=hotel,
                        notification_type=Notification.Type.PRIORITY_EXPIRED,
                        title="🔔 Food Available Now — Claim Before It Expires!",
                        message=(
                            f'"{food.title}" posted by {food.donor.username} is now '
                            f"available for claiming. {food.quantity} servings at "
                            f"{food.location}. Claim it before it expires at {expiry_str}!"
                        ),
                        related_food_post=food,
                    )
                )

        Notification.objects.bulk_create(notifications)
        self.stdout.write(
            self.style.SUCCESS(
                f"Sent {len(notifications)} hotel notifications for "
                f"{expired_window_posts.count()} food post(s)."
            )
        )
