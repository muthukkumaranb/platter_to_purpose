import importlib
import os
from unittest.mock import patch

from django.test import SimpleTestCase

import config.settings.pythonanywhere as pythonanywhere


class PythonAnywhereSettingsTests(SimpleTestCase):
    def test_empty_email_credentials_use_console_backend(self):
        with patch.dict(
            os.environ,
            {"EMAIL_HOST_USER": "", "EMAIL_HOST_PASSWORD": ""},
        ):
            settings = importlib.reload(pythonanywhere)

        self.assertEqual(
            settings.EMAIL_BACKEND,
            "django.core.mail.backends.console.EmailBackend",
        )
