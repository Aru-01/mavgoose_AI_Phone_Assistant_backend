from rest_framework import serializers
from ai_behavior.models import (
    GreetingConfig,
    AIConfig,
    AutoTransferKeyword,
    BusinessHour,
)


class GreetingConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = GreetingConfig
        fields = [
            "opening_hours_greeting",
            "closed_hours_message",
        ]


class BusinessHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessHour
        fields = [
            "day",
            "is_open",
            "open_time",
            "close_time",
        ]


class AutoTransferKeywordCRUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoTransferKeyword
        fields = ["id", "keyword"]
        read_only_fields = ["id"]

    def validate_keyword(self, value):
        value = value.lower().strip()

        ai_config = self.context["ai_config"]

        qs = AutoTransferKeyword.objects.filter(ai_config=ai_config, keyword=value)

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "This keyword already exists for this store."
            )

        return value


class AutoTransferKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoTransferKeyword
        fields = ["keyword"]

    def validate_keyword(self, value):
        return value.lower().strip()


class AIConfigSerializer(serializers.ModelSerializer):
    greetings = GreetingConfigSerializer(required=False)
    business_hours = BusinessHourSerializer(many=True, required=False)
    auto_transfer_keywords = AutoTransferKeywordSerializer(many=True, required=False)

    class Meta:
        model = AIConfig
        fields = [
            "id",
            "store",
            "tone",
            "retry_attempts_before_transfer",
            "fallback_response",
            "greetings",
            "business_hours",
            "auto_transfer_keywords",
        ]
        read_only_fields = ["id", "store"]

    def create(self, validated_data):
        greetings_data = validated_data.pop("greetings", None)
        business_hours_data = validated_data.pop("business_hours", [])
        keywords_data = validated_data.pop("auto_transfer_keywords", [])

        ai_config = AIConfig.objects.create(**validated_data)

        if greetings_data:
            GreetingConfig.objects.create(ai_config=ai_config, **greetings_data)

        for bh in business_hours_data:
            BusinessHour.objects.create(ai_config=ai_config, **bh)

        for kw in keywords_data:
            AutoTransferKeyword.objects.create(ai_config=ai_config, **kw)

        return ai_config

    def update(self, instance, validated_data):
        greetings_data = validated_data.pop("greetings", None)
        business_hours_data = validated_data.pop("business_hours", None)
        keywords_data = validated_data.pop("auto_transfer_keywords", None)

        # Update AIConfig fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Greeting update
        if greetings_data:
            GreetingConfig.objects.update_or_create(
                ai_config=instance,
                defaults=greetings_data,
            )

        # Business hours (replace all)
        if business_hours_data is not None:
            instance.business_hours.all().delete()
            for bh in business_hours_data:
                BusinessHour.objects.create(ai_config=instance, **bh)

        # Keywords (replace all)
        if keywords_data is not None:
            instance.auto_transfer_keywords.all().delete()
            for kw in keywords_data:
                AutoTransferKeyword.objects.create(ai_config=instance, **kw)

        return instance
