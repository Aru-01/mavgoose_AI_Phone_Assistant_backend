from rest_framework.permissions import BasePermission


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
