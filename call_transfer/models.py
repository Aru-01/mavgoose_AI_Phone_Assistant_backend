from django.db import models
from store.models import Store


class ConditionChoices(models.TextChoices):
    SOFTWARE_ISSUE = "SOFTWARE_ISSUE", "Software Issues"
    UNKNOWN_DEVICE = "UNKNOWN_DEVICE", "Unknown Device"
    PRICE_NEGOTIATION = "PRICE_NEGOTIATION", "Price Negotiation"
    WARRANTY_QUESTIONS = "WARRANTY_QUESTIONS", "Warranty Questions"
    ANGRY_CUSTOMER = "ANGRY_CUSTOMER", "Angry Customer Detected"
    OTHER = "OTHER", "Other"


class TransferCondition(models.Model):

    condition = models.CharField(
        max_length=50, choices=ConditionChoices.choices, unique=True
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return self.get_condition_display()


class TransferContact(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="transfer_contacts"
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("store", "phone_number")

    def __str__(self):
        return f"{self.name} ({self.phone_number})"


class CallTransfer(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    condition = models.ForeignKey(
        TransferCondition, on_delete=models.CASCADE, related_name="rules"
    )
    transfer_contact = models.ForeignKey(
        TransferContact, on_delete=models.CASCADE, related_name="rules"
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f" {self.store.name} → {self.condition.get_condition_display()} → {self.transfer_contact.name}"
