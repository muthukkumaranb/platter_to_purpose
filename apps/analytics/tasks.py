import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from apps.analytics.services import award_badges
from apps.analytics.utils import send_monthly_impact_email

logger = logging.getLogger(__name__)


@shared_task
def compute_badges_task(user_id):
    logger.info(f"Computing badges for user {user_id}")
    User = get_user_model()  # noqa: N806
    try:
        user = User.objects.get(pk=user_id)
        badges = award_badges(user)
        logger.info(f"Earned badges count: {len(badges)}")
        return len(badges)
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for badge computation")
        return 0


@shared_task
def send_monthly_report_task():
    logger.info("Running monthly report task for all users")
    User = get_user_model()  # noqa: N806
    users = User.objects.filter(email__isnull=False).exclude(email="")
    sent = 0
    for user in users:
        logger.info(f"Sending monthly report email to {user.username}")
        success = send_monthly_impact_email(user)
        if success:
            sent += 1
    logger.info(f"Monthly report task completed. Emails sent: {sent}")
    return sent
