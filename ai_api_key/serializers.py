from rest_framework import serializers
from ai_api_key.models import APIKey, Speech_to_Text, Model_Configuration


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class Model_Configuration_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Model_Configuration
        fields = "__all__"
        read_only_fields = ("store",)


class STTConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speech_to_Text
        fields = "__all__"
        read_only_fields = ("store",)
