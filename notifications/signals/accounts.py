from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from notifications.models import Notification, NotificationCategory
from notifications.utils import get_recipients


# notifications/signals/accounts.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from accounts.models import User
from notifications.models import Notification, NotificationCategory
from notifications.utils import get_recipients


@receiver(pre_save, sender=User)
def store_old_role(sender, instance, **kwargs):
    if instance.pk:
        instance._old_role = (
            sender.objects.filter(pk=instance.pk).values_list("role", flat=True).first()
        )
    else:
        instance._old_role = None


@receiver(post_save, sender=User, dispatch_uid="user_role_change_notification")
def user_created_or_role_updated(sender, instance, created, **kwargs):
    if not instance.store:
        return

    recipients = get_recipients(instance.store)

    # ✅ User created
    if created:
        title = "New User Added"
        message = (
            f"{instance.get_full_name()} has been added as "
            f"{instance.get_role_display()} for {instance.store.name}"
        )

    # ✅ ONLY role changed
    elif instance._old_role != instance.role:
        title = "User Role Updated"
        message = (
            f"{instance.get_full_name()}'s role updated to "
            f"{instance.get_role_display()}"
        )

    else:
        return  # ❌ no notification for other updates

    for user in recipients:
        Notification.objects.create(
            recipient=user,
            store=instance.store,
            category=NotificationCategory.SYSTEM,
            title=title,
            message=message,
        )
