from django.utils import timezone
from django.db import transaction
from rest_framework import serializers
from callLogs.models import (
    CallSession,
    CallTranscript,
)


class CallTranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallTranscript
        fields = ["speaker", "message", "timestamp"]
        read_only_fields = ["timestamp"]


class CallSessionSerializer(serializers.ModelSerializer):
    transcripts = CallTranscriptSerializer(many=True)
    issue_name = serializers.ReadOnlyField(source="issue.name")

    class Meta:
        model = CallSession
        fields = [
            "id",
            "phone_number",
            "issue",
            "store",
            "issue_name",
            "call_type",
            "outcome",
            "duration",
            "started_at",
            "ended_at",
            "audio_url",
            "transcripts",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        transcripts_data = validated_data.pop("transcripts", [])

        try:
            with transaction.atomic():
                call = CallSession.objects.create(**validated_data)

                transcripts = [
                    CallTranscript(
                        call=call,
                        timestamp=timezone.now(),
                        **t
                    )
                    for t in transcripts_data
                ]

                if transcripts:
                    CallTranscript.objects.bulk_create(transcripts)

            return call

        except Exception as e:
            print("🔥 CREATE ERROR:", e)
            raise
