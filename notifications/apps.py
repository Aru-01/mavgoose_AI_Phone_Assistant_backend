from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"

    def ready(self):
        import notifications.signals.accounts
        import notifications.signals.calls
        import notifications.signals.call_transfer
        import notifications.signals.appointments
