from rest_framework.permissions import BasePermission, SAFE_METHODS
from accounts.models import UserRole


class PriceListPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        # STAFF → read only
        if user.role == UserRole.STAFF:
            return request.method in SAFE_METHODS

        # STORE_MANAGER → full access
        if user.role == UserRole.STORE_MANAGER:
            return True

        # SUPER_ADMIN → full access
        if user.role == UserRole.SUPER_ADMIN:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == UserRole.SUPER_ADMIN:
            return True

        if user.role in [UserRole.STAFF, UserRole.STORE_MANAGER]:
            return obj.store == user.store

        return False


class IsAdminUserRole(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "SUPER_ADMIN"
        )


class IsAdminOrStoreManager(BasePermission):
    """
    Only SUPER_ADMIN or STORE_MANAGER can create/update StoreSchedule.
    Store Manager can only manage schedule of their own store.
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.role in ["SUPER_ADMIN", "STORE_MANAGER"]

    def has_object_permission(self, request, view, obj):
        user = request.user
        # SUPER_ADMIN can do anything
        if user.role == "SUPER_ADMIN":
            return True
        # STORE_MANAGER can only manage own store
        if user.role == "STORE_MANAGER" and hasattr(user, "store"):
            return obj.store == user.store
        return False


from rest_framework.permissions import BasePermission
from store.models import Store


class AIBehaviorPermission(BasePermission):
    """
    Staff / Store Manager → only own store
    Super Admin → all stores
    """

    def has_permission(self, request, view):
        user = request.user

        if user.role == "SUPER_ADMIN":
            return True

        store_id = view.kwargs.get("store_id")

        if not store_id:
            return False

        return user.store_id == int(store_id)
