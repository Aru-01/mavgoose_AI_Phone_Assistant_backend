from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from store.models import Store
from store.serialziers import StoreSerializer
from store.permissions import IsSuperAdmin
from accounts.models import UserRole
from drf_yasg.utils import swagger_auto_schema


class StoreViewSet(ModelViewSet):
    """
    Store API endpoints:

    - **List Stores**: Super Admin can view all stores.
    - **Retrieve Store**: Super Admin can retrieve any store by ID.
    - **Create Store**: Only Super Admin.
    - **Update/Partial Update Store**: Only Super Admin.
    - **Delete Store**: Only Super Admin.
    - **Staff/Store Admin**: Will only see their own store (future update).
    """

    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Super Admin → all stores
        if user.role == UserRole.SUPER_ADMIN:
            return Store.objects.all()

        # # Store admin / staff → only own store
        # return Store.objects.filter(id=user.store_id)
        return {"message:": "unauthorized"}

    def get_permissions(self):
        # Only Super Admin can create/update/delete
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsSuperAdmin()]

        return super().get_permissions()

    @swagger_auto_schema(
        operation_summary="List all stores",
        operation_description="Only Super Admin can view all stores. Staff will see their store (future).",
        responses={200: StoreSerializer(many=True)},
        tags=["api / v1 / stores"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a store",
        operation_description="Retrieve store by ID. Super Admin can retrieve any store.",
        responses={200: StoreSerializer()},
        tags=["api / v1 / stores"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a store",
        operation_description="Only Super Admin can create a store.",
        request_body=StoreSerializer,
        responses={201: StoreSerializer()},
        tags=["api / v1 / stores"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a store",
        operation_description="Only Super Admin can update a store.",
        request_body=StoreSerializer,
        responses={200: StoreSerializer()},
        tags=["api / v1 / stores"],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial update a store",
        operation_description="Only Super Admin can partially update a store.",
        request_body=StoreSerializer,
        responses={200: StoreSerializer()},
        tags=["api / v1 / stores"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a store",
        operation_description="Only Super Admin can delete a store.",
        responses={204: "No Content"},
        tags=["api / v1 / stores"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
