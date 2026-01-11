from django.db.models.signals import post_save
from django.dispatch import receiver
from call_transfer.models import CallTransfer
from notifications.models import Notification, NotificationCategory
from notifications.utils import get_recipients


@receiver(post_save, sender=CallTransfer)
def call_transfer_notification(sender, instance, created, **kwargs):
    if not created:
        return
    if not instance.store or not instance.transfer_contact or not instance.condition:
        return

    recipients = get_recipients(instance.store)

    title = "Warm Transfer Completed"
    message = (
        f"Call successfully transferred to {instance.transfer_contact.name} - "
        f"Customer inquiry about {instance.condition}"
    )

    for user in recipients:
        Notification.objects.create(
            recipient=user,
            store=instance.store,
            category=NotificationCategory.CALLS,
            title=title,
            message=message,
        )
