import logging

from celery import shared_task

from apps.accounts.utils import send_email_otp

logger = logging.getLogger(__name__)


@shared_task
def send_otp_task(email, otp):
    logger.info("Asynchronously dispatching email OTP to %s", email)
    return send_email_otp(email, otp)
