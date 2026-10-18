import logging
import random

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def generate_otp():
    """Generates a 6-digit OTP."""
    return str(random.randint(100000, 999999))


def send_email_otp(email, otp):
    """Send an account verification code to the registered email address."""
    if not email:
        logger.warning("Cannot send OTP because the user has no email address.")
        return False

    send_mail(
        subject="Your Platter to Purpose verification code",
        message=f"Your verification code is: {otp}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
    logger.info("OTP sent by email to %s", email)
    return True
