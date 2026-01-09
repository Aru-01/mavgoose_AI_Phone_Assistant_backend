from django.db import models
from store.models import Store


class APIKey(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="api_keys")
    api_key = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.store.name} - {self.api_key[:8]}..."


class Model_Configuration(models.Model):
    store = models.OneToOneField(
        Store, on_delete=models.CASCADE, related_name="Model_Configuration"
    )

    # Model Configuration
    MODEL_CHOICES = [
        ("GPT-4.0", "GPT-4.0 (Recommend)"),
        ("GPT-3.5-Turbo", "GPT-3.5 Turbo"),
        ("GPT-4", "GPT-4"),
    ]
    model_version = models.CharField(
        max_length=20, choices=MODEL_CHOICES, default="GPT-4.0"
    )
    temperature = models.DecimalField(
        max_digits=3, decimal_places=1, default=0.5
    )  # 0.1-1.0
    max_tokens = models.PositiveIntegerField(default=500)  # 10-500

    # Performance Settings
    response_timeout = models.PositiveIntegerField(default=30)  # seconds
    retry_attempts = models.PositiveSmallIntegerField(default=3)  # 1-5

    # Voice Provider
    VOICE_CHOICES = [
        ("google_tts", "Google TTS"),
        ("eleven_labs", "Eleven Labs"),
        ("amazon_polly", "Amazon Polly"),
    ]
    voice_provider = models.CharField(
        max_length=20, choices=VOICE_CHOICES, default="google_tts"
    )

    def __str__(self):
        return f"{self.store.name} Model Configuration & Performance Settings"


#
class Speech_to_Text(models.Model):
    store = models.OneToOneField(
        Store, on_delete=models.CASCADE, related_name="Speech_to_Text"
    )

    STT_CHOICES = [
        ("google_stt", "Google Speech-to-Text"),
        ("azure_stt", "Azure Speech"),
        ("aws_transcribe", "AWS Transcribe"),
    ]
    stt_provider = models.CharField(
        max_length=20, choices=STT_CHOICES, default="google_stt"
    )

    LANGUAGE_CHOICES = [
        ("english", "English"),
        ("spanish", "Spanish"),
        ("french", "French"),
    ]
    language_model = models.CharField(
        max_length=10, choices=LANGUAGE_CHOICES, default="english"
    )

    punctuation_auto_correction = models.BooleanField(default=True)
    background_noise_suppression = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.store.name} Speech_to_Text Config"
