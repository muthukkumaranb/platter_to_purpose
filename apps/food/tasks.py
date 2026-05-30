import logging
from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.food.models import FoodPost
from apps.notifications.models import Notification

logger = logging.getLogger(__name__)


@shared_task
def notify_priority_expiry_task():
    logger.info("Running notify_priority_expiry_task")
    now = timezone.now()
    lookback = now - timedelta(minutes=5)

    # Find unclaimed food posts whose priority window just expired
    expired_window_posts = FoodPost.objects.filter(
        priority_window_ends__gt=lookback,
        priority_window_ends__lte=now,
        is_claimed=False,
        expiry_time__gt=now,
    )

    if not expired_window_posts.exists():
        logger.info("No newly expired priority windows.")
        return 0

    User = get_user_model()  # noqa: N806
    hotels = User.objects.filter(role="HOTEL")

    if not hotels.exists():
        logger.warning("No hotel users found.")
        return 0

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
    logger.info(
        f"Sent {len(notifications)} hotel notifications for {expired_window_posts.count()} food post(s)."
    )
    return len(notifications)
