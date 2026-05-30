import logging

from django.conf import settings
from django.core.mail import send_mail

# Set up logger so email failures are logged but don't crash the app
logger = logging.getLogger(__name__)


def send_notification_email(user, subject, message):
    """
    Send an email notification to a user.

    - Checks that the user has a valid email address before attempting to send.
    - Catches all exceptions gracefully so that email failures never
      break the main application flow.
    - Uses Django's built-in send_mail, which works with any configured
      email backend (console, SMTP, SendGrid, etc.)

    Args:
        user: The User instance to send the email to.
        subject: Email subject line.
        message: Plain-text email body.
    """
    # Skip if user has no email address
    if not user.email:
        logger.warning(
            f"Skipping email for user '{user.username}' — no email address on file."
        )
        return False

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,  # We handle exceptions ourselves
        )
        logger.info(f"Email sent to {user.email}: {subject}")
        return True
    except Exception as e:
        # Log the error but don't crash — the in-app notification is already saved
        logger.error(f"Failed to send email to {user.email}: {e}")
        return False
