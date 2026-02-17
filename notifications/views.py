from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from notifications.models import Notification
from notifications.serializers import NotificationSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class NotificationListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    @swagger_auto_schema(
        tags=["Notification"],
        manual_parameters=[
            openapi.Parameter(
                "category",
                openapi.IN_QUERY,
                description="Filter by category (CALLS, SYSTEM, USER, APPOINTMENT)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Filter by read status (read, unread, all)",
                type=openapi.TYPE_STRING,
                enum=["read", "unread", "all"],
            ),
        ],
        responses={200: NotificationSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user

        qs = Notification.objects.filter(recipient=user)

        category = self.request.query_params.get("category")
        status = self.request.query_params.get("status")

        if category:
            qs = qs.filter(category=category)

        if status == "read":
            qs = qs.filter(is_read=True)
        elif status == "unread":
            qs = qs.filter(is_read=False)

        return qs.order_by("-created_at")


class NotificationMarkReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Notification"],
        operation_summary="Mark notification as read",
        operation_description="Marks a single notification as read for the logged-in user.",
        responses={
            200: openapi.Response(
                description="Notification marked as read",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Notification marked as read",
                    }
                },
            ),
            404: "Notification not found",
        },
    )
    def patch(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)

        notification.is_read = True
        notification.save(update_fields=["is_read"])

        return Response({"success": True, "message": "Notification marked as read"})


class NotificationDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
