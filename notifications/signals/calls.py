# notifications/signals/calls.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from callLogs.models import CallSession
from notifications.models import Notification, NotificationCategory
from notifications.utils import get_recipients


@receiver(post_save, sender=CallSession)
def call_log_notification(sender, instance, created, **kwargs):
    if not created:
        return

    recipients = get_recipients(instance.store)

    if instance.call_type == "AI_RESOLVED":
        title = "AI Resolved Call Completed"
        message = "AI successfully resolved the customer call."

    elif instance.call_type == "WARM_TRANSFER":
        title = "Warm Transfer Completed"
        message = (
            f"Call successfully transferred to "
            f"{instance.transferred_to} - {instance.issue_summary}"
        )
    else:
        return

    for user in recipients:
        Notification.objects.create(
            recipient=user,
            store=instance.store,
            category=NotificationCategory.CALLS,
            title=title,
            message=message,
        )
