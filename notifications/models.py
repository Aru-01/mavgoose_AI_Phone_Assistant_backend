from django.db import models
from django.conf import settings
from store.models import Store


class NotificationCategory(models.TextChoices):
    CALLS = "CALLS", "Calls"
    SYSTEM = "SYSTEM", "System"
    USER = "USER", "User"
    APPOINTMENT = "APPOINTMENT", "Appointment"

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=255)
    message = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=NotificationCategory.choices,
    )

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} → {self.recipient}"
