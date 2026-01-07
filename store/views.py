from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from store.models import Store
from store.serialziers import StoreSerializer
from store.permissions import IsSuperAdmin
from accounts.models import UserRole


class StoreViewSet(ModelViewSet):
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
