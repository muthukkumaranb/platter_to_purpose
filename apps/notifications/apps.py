from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"
    label = "notifications"

    def ready(self):
        """
        Import signals module when the app is ready.
        This ensures our signal handlers are connected on startup.
        """
        import apps.notifications.signals  # noqa: F401
