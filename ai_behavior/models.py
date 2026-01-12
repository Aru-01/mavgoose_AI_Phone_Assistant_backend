from django.db import models
from store.models import Store


class AIBehaviorConfig(models.Model):
    store = models.OneToOneField(
        Store, on_delete=models.CASCADE, related_name="ai_behavior_config"
    )

    # Tone & Personality
    tone = models.CharField(
        max_length=30,
        choices=[
            ("friendly", "Friendly & Warm"),
            ("professional", "Professional"),
            ("sales", "Sales-Oriented"),
        ],
        default="friendly",
    )
    # Escalation Rules
    retry_attempts_before_transfer = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        default=3,
    )

    fallback_response = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class GreetingConfig(models.Model):
    ai_behavior_config = models.OneToOneField(
        AIBehaviorConfig, on_delete=models.CASCADE, related_name="greetings"
    )

    opening_hours_greeting = models.TextField()
    closed_hours_message = models.TextField()


class BusinessHour(models.Model):
    ai_behavior_config = models.ForeignKey(
        AIBehaviorConfig, on_delete=models.CASCADE, related_name="business_hours"
    )

    day = models.PositiveSmallIntegerField(
        choices=[
            (0, "Monday"),
            (1, "Tuesday"),
            (2, "Wednesday"),
            (3, "Thursday"),
            (4, "Friday"),
            (5, "Saturday"),
            (6, "Sunday"),
        ]
    )

    is_open = models.BooleanField(default=True)
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ("ai_behavior_config", "day")

    def __str__(self):
        return f"{self.get_day_display()} - {'Open' if self.is_open else 'Closed'}"


class AutoTransferKeyword(models.Model):
    ai_behavior_config = models.ForeignKey(
        AIBehaviorConfig,
        on_delete=models.CASCADE,
        related_name="auto_transfer_keywords",
    )

    keyword = models.CharField(max_length=150)

    class Meta:
        unique_together = ("ai_behavior_config", "keyword")
