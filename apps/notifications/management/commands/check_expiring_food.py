"""
Management command: check_expiring_food

Finds food posts that are:
  - NOT claimed
  - Expiring within the next 1 hour
  - Haven't already been notified (to avoid duplicate alerts)

Creates an in-app notification + sends an email to the donor.

Usage:
  python manage.py check_expiring_food

In production, schedule this to run every 15-30 minutes via:
  - cron job (Linux)
  - Render Cron Jobs (free tier)
  - Windows Task Scheduler
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.food.models import FoodPost
from apps.notifications.models import Notification
from apps.notifications.utils import send_notification_email


class Command(BaseCommand):
    help = "Check for food posts expiring within 1 hour and notify donors."

    def handle(self, *args, **options):
        now = timezone.now()
        one_hour_later = now + timedelta(hours=1)

        # Find unclaimed food posts expiring within the next hour
        expiring_posts = FoodPost.objects.filter(
            is_claimed=False,
            expiry_time__isnull=False,
            expiry_time__gt=now,  # Not already expired
            expiry_time__lte=one_hour_later,  # Expiring within 1 hour
        )

        notified_count = 0

        for food in expiring_posts:
            # Check if we already sent an expiring notification for this food post
            already_notified = Notification.objects.filter(
                related_food_post=food,
                notification_type=Notification.Type.FOOD_EXPIRING,
            ).exists()

            if already_notified:
                continue  # Skip — already alerted for this post

            # Calculate minutes remaining
            minutes_left = int((food.expiry_time - now).total_seconds() / 60)

            # Create in-app notification for the donor
            Notification.objects.create(
                user=food.donor,
                notification_type=Notification.Type.FOOD_EXPIRING,
                title=f"⏰ Your food is expiring soon: {food.title}",
                message=(
                    f'Your food post "{food.title}" will expire in '
                    f"approximately {minutes_left} minutes. "
                    f"Consider extending the expiry or removing the post."
                ),
                related_food_post=food,
            )

            # Send email to the donor
            send_notification_email(
                user=food.donor,
                subject=f"[Platter to Purpose] Food Expiring Soon: {food.title}",
                message=(
                    f"Hi {food.donor.username},\n\n"
                    f'Your food post "{food.title}" will expire in '
                    f"approximately {minutes_left} minutes.\n\n"
                    f"If it hasn't been claimed yet, you may want to extend "
                    f"the expiry time or remove the listing.\n\n"
                    f"— Platter to Purpose"
                ),
            )

            notified_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Notified {notified_count} donor(s) about expiring food."
            )
        )
