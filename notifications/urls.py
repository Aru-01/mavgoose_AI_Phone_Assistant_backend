from django.urls import path
from notifications.views import (
    NotificationListAPIView,
    NotificationMarkReadAPIView,
    NotificationDeleteAPIView,
)

urlpatterns = [
    path("", NotificationListAPIView.as_view(), name="notification-list"),
    path(
        "<int:pk>/delete/",
        NotificationDeleteAPIView.as_view(),
        name="notification-delete",
    ),
    path(
        "<int:pk>/read/",
        NotificationMarkReadAPIView.as_view(),
        name="notification-mark-read",
    ),
]
