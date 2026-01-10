from django.db.models import Q
from accounts.models import User, UserRole


def get_recipients(store):
    return User.objects.filter(Q(role=UserRole.SUPER_ADMIN) | Q(store=store)).filter(
        is_active=True
    )
