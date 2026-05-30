import logging

from celery import shared_task

from apps.accounts.utils import send_whatsapp_otp

logger = logging.getLogger(__name__)


@shared_task
def send_otp_task(phone_number, otp):
    logger.info(f"Asynchronously dispatching WhatsApp OTP to {phone_number}")
    return send_whatsapp_otp(phone_number, otp)
