from django.db import models
from price_list.models import RepairType
from store.models import Store


class CallOutcome(models.TextChoices):
    QUOTE_PROVIDED = "QUOTE_PROVIDED", "Quote Provided"
    APPOINTMENT_BOOKED = "APPOINTMENT_BOOKED", "Appointment Booked"
    ESCALATED = "ESCALATED", "Escalated to Technician"
    CALL_DROPPED = "CALL_DROPPED", "Call Dropped"


class CallType(models.TextChoices):
    AI_RESOLVED = "AI_RESOLVED", "AI Resolved"
    WARM_TRANSFER = "WARM_TRANSFER", "Warm Transfer"
    DROPPED = "DROPPED", "Dropped"
    APPOINTMENT = "APPOINTMENT", "Appointment"


class Speaker(models.TextChoices):
    AI = "AI", "AI"
    CUSTOMER = "CUSTOMER", "Customer"


class CallSession(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="calls")
    phone_number = models.CharField(max_length=20)
    issue = models.ForeignKey(
        RepairType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="calls",
    )
    call_type = models.CharField(max_length=20, choices=CallType.choices)

    outcome = models.CharField(
        max_length=30, choices=CallOutcome.choices, null=True, blank=True
    )
    duration = models.CharField(max_length=10)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    audio_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone_number} - {self.call_type}"


class CallTranscript(models.Model):
    call = models.ForeignKey(
        CallSession, related_name="transcripts", on_delete=models.CASCADE
    )
    speaker = models.CharField(max_length=10, choices=Speaker.choices)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.speaker}: {self.message[:30]}"
