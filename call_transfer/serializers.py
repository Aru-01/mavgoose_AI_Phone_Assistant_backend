from rest_framework import serializers
from .models import TransferCondition, TransferContact, StoreTransferRule


class TransferConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferCondition
        fields = ["id", "condition", "description"]


class TransferContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferContact
        fields = ["id", "store", "name", "phone_number", "is_active"]


class StoreTransferRuleSerializer(serializers.ModelSerializer):
    condition = TransferConditionSerializer(read_only=True)
    condition_id = serializers.PrimaryKeyRelatedField(
        queryset=TransferCondition.objects.all(), source="condition", write_only=True
    )

    transfer_contact = TransferContactSerializer(read_only=True)
    transfer_contact_id = serializers.PrimaryKeyRelatedField(
        queryset=TransferContact.objects.filter(is_active=True),
        source="transfer_contact",
        write_only=True,
    )

    class Meta:
        model = StoreTransferRule
        fields = [
            "id",
            "condition",
            "condition_id",
            "transfer_contact",
            "transfer_contact_id",
            "is_active",
        ]
