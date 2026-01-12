# notifications/signals/appointments.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from appointments.models import Appointment
from notifications.models import Notification, NotificationCategory
from notifications.utils import get_recipients


@receiver(post_save, sender=Appointment)
def appointment_created_notification(sender, instance, created, **kwargs):
    if not created:
        return  # only new appointment

    if not instance.store:
        return

    recipients = get_recipients(instance.store)

    title = "New Appointment Booked"
    message = (
        f"Client: {instance.client_name} | Email: {instance.client_email} | "
        f"Phone: {instance.client_phone} | Repair Type: {instance.repair_type.name} | "
        f"Category: {instance.category.name} | Brand: {instance.brand.name} | "
        f"Model: {instance.device_model.name} | Date: {instance.date} | "
        f"Start Time: {instance.start_time} | Serial No: {instance.serial_no}"
    )

    for user in recipients:
        Notification.objects.create(
            recipient=user,
            store=instance.store,
            category=NotificationCategory.APPOINTMENT,
            title=title,
            message=message,
        )
