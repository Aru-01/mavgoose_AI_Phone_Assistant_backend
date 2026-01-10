from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from notifications.models import Notification, NotificationCategory
from notifications.utils import get_recipients


@receiver(post_save, sender=User)
def user_created_or_updated(sender, instance, created, **kwargs):
    if not instance.store:
        return

    recipients = get_recipients(instance.store)

    if created:
        title = "New User Added"
        message = (
            f"{instance.get_full_name()} has been added as "
            f"{instance.get_role_display()} for {instance.store.name}"
        )
    else:
        title = "User Role Updated"
        message = (
            f"{instance.get_full_name()}'s role updated to "
            f"{instance.get_role_display()}"
        )

    for user in recipients:
        Notification.objects.create(
            recipient=user,
            store=instance.store,
            category=NotificationCategory.SYSTEM,
            title=title,
            message=message,
        )
