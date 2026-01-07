from rest_framework import viewsets
from call_transfer.models import TransferCondition, TransferContact, StoreTransferRule
from call_transfer.serializers import (
    TransferConditionSerializer,
    TransferContactSerializer,
    StoreTransferRuleSerializer,
)
from api.permissions import IsAdminUserRole


class TransferConditionViewSet(viewsets.ModelViewSet):
    queryset = TransferCondition.objects.all()
    serializer_class = TransferConditionSerializer
    permission_classes = [IsAdminUserRole]
    http_method_names = ["get", "post", "put", "patch", "delete"]


class TransferContactViewSet(viewsets.ModelViewSet):
    queryset = TransferContact.objects.all()
    serializer_class = TransferContactSerializer
    permission_classes = [IsAdminUserRole]
    http_method_names = ["get", "post", "put", "patch", "delete"]

    def get_queryset(self):
        qs = super().get_queryset()
        store_id = self.request.query_params.get("store")
        if store_id:
            qs = qs.filter(store_id=store_id)
        return qs


class StoreTransferRuleViewSet(viewsets.ModelViewSet):
    queryset = StoreTransferRule.objects.select_related(
        "condition", "transfer_contact", "transfer_contact__store"
    ).all()
    serializer_class = StoreTransferRuleSerializer
    permission_classes = [IsAdminUserRole]
    http_method_names = ["get", "post", "put", "patch", "delete"]

    def get_queryset(self):
        qs = super().get_queryset()
        store_id = self.request.query_params.get("store")
        if store_id:
            qs = qs.filter(transfer_contact__store_id=store_id)
        return qs
