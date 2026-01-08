from rest_framework import viewsets
from call_transfer.models import TransferCondition, TransferContact, StoreTransferRule
from call_transfer.serializers import (
    TransferConditionSerializer,
    TransferContactSerializer,
    StoreTransferRuleSerializer,
)
from api.permissions import IsAdminUserRole
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class TransferConditionViewSet(viewsets.ModelViewSet):
    """
    Transfer Condition API
    - List / Retrieve / Create / Update / Delete conditions
    """

    queryset = TransferCondition.objects.all()
    serializer_class = TransferConditionSerializer
    permission_classes = [IsAdminUserRole]
    http_method_names = ["get", "put", "patch", "delete"]

    @swagger_auto_schema(
        operation_summary="List all transfer conditions",
        tags=["Call Transfer - Conditions"],
        responses={200: TransferConditionSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a transfer condition",
        tags=["Call Transfer - Conditions"],
        responses={200: TransferConditionSerializer()},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a transfer conditions",
        operation_description="Update a transfer conditions.",
        request_body=TransferConditionSerializer,
        responses={200: TransferConditionSerializer()},
        tags=["Call Transfer - Conditions"],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial update a transfer conditions",
        operation_description="Partial update a transfer conditions.",
        request_body=TransferConditionSerializer,
        responses={200: TransferConditionSerializer()},
        tags=["Call Transfer - Conditions"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a transfer conditions",
        operation_description="Delete a transfer conditions.",
        request_body=TransferConditionSerializer,
        responses={204: TransferConditionSerializer()},
        tags=["Call Transfer - Conditions"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class TransferContactViewSet(viewsets.ModelViewSet):
    """
    Transfer Contact API
    - List / Retrieve / Create / Update / Delete contacts
    """

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
