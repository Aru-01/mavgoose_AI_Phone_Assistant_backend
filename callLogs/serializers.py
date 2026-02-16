from django.utils import timezone
from django.db import transaction
from rest_framework import serializers
from callLogs.models import (
    CallSession,
    CallTranscript,
)
from price_list.models import RepairType


class CallTranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallTranscript
        fields = ["speaker", "message", "timestamp"]
        read_only_fields = ["timestamp"]


class CallSessionSerializer(serializers.ModelSerializer):
    transcripts = CallTranscriptSerializer(many=True, required=False)
    issue_name = serializers.ReadOnlyField(source="issue.name")
    issue = serializers.CharField(required=False, allow_blank=True)

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
        issue_name = validated_data.pop("issue", None)

        if issue_name:
            try:
                repair_type = RepairType.objects.get(name__iexact=issue_name)
                validated_data["issue"] = repair_type
            except RepairType.DoesNotExist:
                validated_data["issue"] = None

        try:
            with transaction.atomic():
                call = CallSession.objects.create(**validated_data)

                if transcripts_data:
                    transcripts = [
                        CallTranscript(call=call, timestamp=timezone.now(), **t)
                        for t in transcripts_data
                    ]
                    CallTranscript.objects.bulk_create(transcripts)

            return call

        except Exception as e:
            print("🔥 CREATE ERROR:", e)
            raise


class StoreCallSummarySerializer(serializers.Serializer):
    store_id = serializers.IntegerField()
    store_name = serializers.CharField()
    total_calls_today = serializers.IntegerField()
    ai_handled = serializers.IntegerField()
    warm_transfer = serializers.IntegerField()
    appointments_booked = serializers.IntegerField()
    missed_calls = serializers.IntegerField()
    avg_call_duration = serializers.FloatField()
