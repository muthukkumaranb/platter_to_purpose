import logging
import random

logger = logging.getLogger(__name__)


def generate_otp():
    """Generates a 6-digit OTP."""
    return str(random.randint(100000, 999999))


def send_whatsapp_otp(phone_number, otp):
    """
    Sends the OTP to the given phone number via WhatsApp.
    This is a mock implementation. To use a real service like Twilio:
    1. Install twilio: pip install twilio
    2. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER in settings
    """
    message = f"Your Platter Verification Code is: {otp}"

    # --- MOCK IMPLEMENTATION (For Development) ---
    print(f"\n{'=' * 30}")
    print(f" [MOCK WHATSAPP] To: {phone_number}")
    print(f" Message: {message}")
    print(f"{'=' * 30}\n")
    logger.info(f"OTP sent to {phone_number}: {otp}")

    # --- PROD IMPLEMENTATION (Twilio Example) ---
    # from django.conf import settings
    # from twilio.rest import Client
    # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    # message = client.messages.create(
    #     body=message,
    #     from_=settings.TWILIO_WHATSAPP_NUMBER, # e.g., 'whatsapp:+14155238886'
    #     to=f'whatsapp:{phone_number}'
    # )
    # return message.sid

    return True
