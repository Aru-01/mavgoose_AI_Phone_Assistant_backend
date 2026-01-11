from rest_framework import serializers
from call_transfer.models import TransferCondition, TransferContact, CallTransfer
from store.models import Store


class TransferConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferCondition
        fields = ["id", "condition", "description"]


class TransferContactSerializer(serializers.ModelSerializer):
    store = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(),
        required=False,
    )

    class Meta:
        model = TransferContact
        fields = ["id", "store", "name", "phone_number", "is_active"]


class CallTransferSerializer(serializers.ModelSerializer):
    condition = TransferConditionSerializer(read_only=True)
    condition_id = serializers.PrimaryKeyRelatedField(
        queryset=TransferCondition.objects.all(),
        source="condition",
        write_only=True,
    )

    transfer_contact = TransferContactSerializer(read_only=True)
    transfer_contact_id = serializers.PrimaryKeyRelatedField(
        queryset=TransferContact.objects.none(),  # dynamic
        source="transfer_contact",
        write_only=True,
    )

    store = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(), write_only=True
    )
    store_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CallTransfer
        fields = [
            "id",
            "store",
            "store_detail",
            "condition",
            "condition_id",
            "transfer_contact",
            "transfer_contact_id",
            "is_active",
        ]

    def get_store_detail(self, obj):
        return {"id": obj.store.id, "name": obj.store.name}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method in ["POST"]:
            store_id = request.data.get("store")
            if store_id:
                self.fields["transfer_contact_id"].queryset = (
                    TransferContact.objects.filter(store_id=store_id, is_active=True)
                )

    def validate(self, attrs):
        store = attrs.get("store")
        transfer_contact = attrs.get("transfer_contact")

        if transfer_contact.store_id != store.id:
            raise serializers.ValidationError(
                "Transfer contact must belong to the same store."
            )
        return attrs
