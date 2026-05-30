"""
Management command to send monthly impact report emails.

Usage:
    python manage.py send_monthly_report

Schedule with cron (run on 1st of each month at 8 AM):
    0 8 1 * * cd /path/to/project && python manage.py send_monthly_report

In development, emails print to the console (console backend).
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.analytics.utils import send_monthly_impact_email

User = get_user_model()


class Command(BaseCommand):
    help = "Send monthly impact report emails to all users with email addresses."

    def handle(self, *args, **options):
        # Only send to users who have an email address
        users = User.objects.filter(email__isnull=False).exclude(email="")
        sent = 0
        failed = 0

        for user in users:
            self.stdout.write(f"Sending to {user.username} ({user.email})...")
            success = send_monthly_impact_email(user)
            if success:
                sent += 1
            else:
                failed += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done! Sent: {sent}, Failed: {failed}, Total: {sent + failed}"
            )
        )
