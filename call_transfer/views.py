from rest_framework import viewsets, response, permissions, status
from call_transfer.models import TransferCondition, TransferContact, CallTransfer
from call_transfer.serializers import (
    TransferConditionSerializer,
    TransferContactSerializer,
    CallTransferSerializer,
)
from accounts.models import UserRole
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
    Transfer Contact API:
    - Staff: view only
    - Store Manager: update their store's contact
    - Super Admin: full access, store-wise filter
    - Each store can have only 1 transfer contact
    """

    queryset = TransferContact.objects.all()
    serializer_class = TransferContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "put"]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        if user.role in [UserRole.STAFF, UserRole.STORE_MANAGER]:
            qs = qs.filter(store=user.store)
        elif user.role == UserRole.SUPER_ADMIN:
            store_id = self.request.query_params.get("store")
            if store_id:
                qs = qs.filter(store_id=store_id)
        return qs

    @swagger_auto_schema(
        operation_summary="List transfer contacts",
        operation_description="Staff can view their store contact. Super Admin can filter by store using query param `store`.",
        tags=["Call Transfer - Contact"],
        manual_parameters=[
            openapi.Parameter(
                "store",
                openapi.IN_QUERY,
                description="Store ID filter (Super Admin only)",
                type=openapi.TYPE_INTEGER,
                required=False,
            )
        ],
        responses={200: TransferContactSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a transfer contact",
        operation_description="Get details of a transfer contact by ID",
        tags=["Call Transfer - Contact"],
        responses={200: TransferContactSerializer()},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create or update transfer contact",
        operation_description=(
            "Each store can have only 1 transfer contact. "
            "Store Manager can create/update their store contact. "
            "Super Admin can create/update any store contact by providing `store` in request body."
        ),
        request_body=TransferContactSerializer,
        responses={
            201: TransferContactSerializer(),
            200: TransferContactSerializer(),
            403: "Permission denied",
            400: "Store required for Super Admin",
        },
        tags=["Call Transfer - Contact"],
    )
    def create(self, request, *args, **kwargs):
        user = request.user
        if user.role not in [UserRole.STORE_MANAGER, UserRole.SUPER_ADMIN]:
            return response.Response({"detail": "Permission denied"}, status=403)

        if user.role == UserRole.STORE_MANAGER:
            store_id = user.store.id
        else:
            store_id = request.data.get("store")
            if not store_id:
                return response.Response(
                    {"store": "Store is required for super admin"}, status=400
                )

        existing_contact = TransferContact.objects.filter(store_id=store_id).first()
        if existing_contact:
            serializer = self.get_serializer(
                existing_contact, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)

        data = request.data.copy()
        data["store"] = store_id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @swagger_auto_schema(
        operation_summary="Update a transfer contact",
        operation_description=(
            "Update name, phone number or is_active of the contact. "
            "Store ID cannot be changed. Store Manager can update their store contact. "
            "Super Admin can update any store contact."
        ),
        request_body=TransferContactSerializer,
        responses={200: TransferContactSerializer(), 403: "Permission denied"},
        tags=["Call Transfer - Contact"],
    )
    def update(self, request, *args, **kwargs):
        user = request.user
        if user.role not in [UserRole.STORE_MANAGER, UserRole.SUPER_ADMIN]:
            return response.Response({"detail": "Permission denied"}, status=403)
        data = request.data.copy()
        data.pop("store", None)
        serializer = self.get_serializer(
            self.get_object(), data=data, partial=kwargs.get("partial", False)
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return response.Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Partial update a transfer contact",
        operation_description="Partial update: name, phone number, or is_active. Store cannot be changed.",
        request_body=TransferContactSerializer,
        responses={200: TransferContactSerializer(), 403: "Permission denied"},
        tags=["Call Transfer - Contact"],
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


class CallTransferViewSet(viewsets.ModelViewSet):
    """
    Call Transfer API
    - Store-scoped transfer rules
    - Only active contacts for the store can be selected
    """

    queryset = CallTransfer.objects.select_related(
        "store", "condition", "transfer_contact", "transfer_contact__store"
    ).all()
    serializer_class = CallTransferSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete"]

    post_request_example = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["store", "condition_id", "transfer_contact_id"],
        properties={
            "store": openapi.Schema(type=openapi.TYPE_INTEGER, description="Store ID"),
            "condition_id": openapi.Schema(
                type=openapi.TYPE_INTEGER, description="Condition ID"
            ),
            "transfer_contact_id": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Transfer Contact ID (must belong to store)",
            ),
            "is_active": openapi.Schema(
                type=openapi.TYPE_BOOLEAN, description="Active status (default True)"
            ),
        },
        example={
            "store": 2,
            "condition_id": 1,
            "transfer_contact_id": 5,
            "is_active": True,
        },
    )

    @swagger_auto_schema(
        operation_summary="List Call Transfers",
        operation_description="Retrieve all call transfer rules. Staff/Manager sees only their store, SuperAdmin can filter by store.",
        tags=["Call - Transfer"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create Call Transfer",
        operation_description="Create a new call transfer rule. Transfer contact must belong to the same store.",
        request_body=post_request_example,
        tags=["Call - Transfer"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve Call Transfer",
        operation_description="Get details of a single call transfer.",
        tags=["Call - Transfer"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete Call Transfer",
        operation_description="Delete a call transfer rule by ID.",
        tags=["Call - Transfer"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        if user.role in [UserRole.STAFF, UserRole.STORE_MANAGER]:
            qs = qs.filter(store=user.store)
        elif user.role == UserRole.SUPER_ADMIN:
            store_id = self.request.query_params.get("store")
            if store_id:
                qs = qs.filter(store_id=store_id)
        return qs
