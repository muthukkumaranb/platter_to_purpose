import logging
from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.food.models import FoodPost
from apps.notifications.models import Notification
from apps.notifications.utils import send_notification_email

logger = logging.getLogger(__name__)


@shared_task
def send_notification_email_task(user_id, subject, message):
    logger.info(f"Asynchronously sending email to user {user_id}")
    User = get_user_model()  # noqa: N806
    try:
        user = User.objects.get(pk=user_id)
        return send_notification_email(user, subject, message)
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for sending email")
        return False


@shared_task
def check_expiring_food_task():
    logger.info("Running check_expiring_food_task")
    now = timezone.now()
    one_hour_later = now + timedelta(hours=1)

    expiring_posts = FoodPost.objects.filter(
        is_claimed=False,
        expiry_time__isnull=False,
        expiry_time__gt=now,
        expiry_time__lte=one_hour_later,
    )

    notified_count = 0
    for food in expiring_posts:
        already_notified = Notification.objects.filter(
            related_food_post=food,
            notification_type=Notification.Type.FOOD_EXPIRING,
        ).exists()

        if already_notified:
            continue

        minutes_left = int((food.expiry_time - now).total_seconds() / 60)

        # Create in-app notification
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

        # Trigger email via task
        send_notification_email_task.delay(
            food.donor.id,
            f"[Platter to Purpose] Food Expiring Soon: {food.title}",
            (
                f"Hi {food.donor.username},\n\n"
                f'Your food post "{food.title}" will expire in '
                f"approximately {minutes_left} minutes.\n\n"
                f"If it hasn't been claimed yet, you may want to extend "
                f"the expiry time or remove the listing.\n\n"
                f"— Platter to Purpose"
            ),
        )
        notified_count += 1

    logger.info(f"Done. Notified {notified_count} donor(s) about expiring food.")
    return notified_count
