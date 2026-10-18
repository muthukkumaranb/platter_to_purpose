"""
View tests for the accounts app.
"""

from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.constants import UserRole
from apps.accounts.models import User


class AccountsViewTests(TestCase):
    def setUp(self):
        self.demo_hotel = User.objects.create(
            username="demo_hotel",
            role=UserRole.HOTEL,
            is_demo=True,
            is_active=True,
        )
        self.demo_hotel.set_unusable_password()
        self.demo_hotel.save()
        self.demo_orphanage = User.objects.create(
            username="demo_orphanage",
            role=UserRole.ORPHANAGE,
            is_demo=True,
            is_active=True,
        )
        self.demo_orphanage.set_unusable_password()
        self.demo_orphanage.save()

    @override_settings(DEMO_MODE=False)
    def test_demo_login_is_not_available_when_disabled(self):
        response = self.client.post(
            reverse("demo_login", kwargs={"role": UserRole.HOTEL})
        )
        self.assertEqual(response.status_code, 404)

    @override_settings(DEMO_MODE=True)
    def test_pythonanywhere_login_page_shows_demo_buttons(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, "Try as Hotel")
        self.assertContains(response, "Try as Orphanage")

    @override_settings(DEMO_MODE=True)
    def test_demo_login_works_for_each_role(self):
        for role in (UserRole.HOTEL, UserRole.ORPHANAGE):
            response = self.client.post(
                reverse("demo_login", kwargs={"role": role})
            )
            self.assertRedirects(response, reverse("dashboard"))
            self.assertEqual(int(self.client.session["_auth_user_id"]), User.objects.get(
                role=role, is_demo=True
            ).pk)

    def test_demo_users_cannot_use_privileged_flags(self):
        self.assertFalse(self.demo_hotel.is_staff)
        self.assertFalse(self.demo_hotel.is_superuser)
        self.assertFalse(self.demo_hotel.has_usable_password())
        self.assertFalse(
            self.client.login(username=self.demo_hotel.username, password="anything")
        )

    @override_settings(DEMO_MODE=True)
    def test_demo_login_is_rate_limited_per_ip(self):
        url = reverse("demo_login", kwargs={"role": UserRole.HOTEL})
        for _ in range(20):
            self.client.post(url, REMOTE_ADDR="203.0.113.10")
        response = self.client.post(url, REMOTE_ADDR="203.0.113.10")
        self.assertEqual(response.status_code, 429)

    @patch("apps.accounts.views.send_email_otp")
    def test_registration_requires_email_otp(self, send_email_otp):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "pending-email-user",
                "email": "pending@example.com",
                "password1": "valid-password-123",
                "password2": "valid-password-123",
                "role": UserRole.HOTEL,
                "phone": "",
                "address": "",
            },
        )
        self.assertRedirects(response, reverse("verify_otp"))
        user = User.objects.get(username="pending-email-user")
        self.assertFalse(user.is_active)
        send_email_otp.assert_called_once()
        self.assertEqual(send_email_otp.call_args.args[0], "pending@example.com")

    @override_settings(
        DEMO_MODE=True,
        EMAIL_HOST_USER="",
        EMAIL_HOST_PASSWORD="",
        EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend",
    )
    def test_signup_notice_is_shown_without_demo_email_credentials(self):
        response = self.client.get(reverse("signup"))

        self.assertContains(
            response,
            "Email sign-up is disabled in this public demo.",
        )
        self.assertContains(response, "Please use the")
        self.assertContains(response, "disabled")

    @override_settings(
        DEMO_MODE=True,
        EMAIL_HOST_USER="",
        EMAIL_HOST_PASSWORD="",
        EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend",
    )
    @patch("apps.accounts.views.send_email_otp")
    def test_signup_without_email_credentials_does_not_return_500(
        self, send_email_otp
    ):
        send_email_otp.side_effect = RuntimeError("mail unavailable")

        response = self.client.post(
            reverse("signup"),
            {
                "username": "pythonanywhere-user",
                "email": "pythonanywhere@example.com",
                "password1": "valid-password-123",
                "password2": "valid-password-123",
                "role": UserRole.HOTEL,
                "phone": "",
                "address": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("verify_otp"))

    @patch("apps.accounts.api.views.send_otp_task.delay")
    def test_api_registration_mail_failure_does_not_return_500(self, delay):
        delay.side_effect = RuntimeError("mail unavailable")
        response = APIClient().post(
            reverse("api_register"),
            {
                "username": "api-mail-failure-user",
                "email": "api-failure@example.com",
                "password": "valid-password-123",
                "role": UserRole.HOTEL,
                "phone": "",
                "address": "",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn("couldn't send", response.data["message"])

    def test_inactive_normal_user_cannot_log_in_before_otp(self):
        user = User.objects.create_user(
            username="pending-user",
            password="valid-password-123",
            role=UserRole.HOTEL,
            is_active=False,
        )
        response = self.client.post(
            reverse("login"),
            {"username": user.username, "password": "valid-password-123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
