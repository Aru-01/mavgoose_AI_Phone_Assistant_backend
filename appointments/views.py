from rest_framework import generics, permissions, serializers
from rest_framework.response import Response
from appointments.models import StoreSchedule, Appointment, generate_available_slots
from appointments.serializers import (
    StoreScheduleSerializer,
    AppointmentSerializer,
    AvailableSlotSerializer,
)
from api.permissions import IsAdminOrStoreManager
from datetime import date
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class StoreScheduleListCreateView(generics.ListCreateAPIView):
    serializer_class = StoreScheduleSerializer
    permission_classes = [IsAdminOrStoreManager]

    @swagger_auto_schema(
        operation_summary="List store schedules",
        operation_description="List store schedules based on user role",
        tags=["Appointments"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create store schedule",
        operation_description="Create a store schedule (Admin / Store Manager only)",
        tags=["Appointments"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        base_qs = StoreSchedule.objects.select_related("store")

        if user.role == "SUPER_ADMIN":
            return base_qs

        elif user.role == "STORE_MANAGER" and hasattr(user, "store"):
            return base_qs.filter(store=user.store)

        return StoreSchedule.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == "SUPER_ADMIN":
            serializer.save()
        elif user.role == "STORE_MANAGER" and hasattr(user, "store"):
            serializer.save(store=user.store)


class StoreScheduleRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = StoreSchedule.objects.all()
    serializer_class = StoreScheduleSerializer
    permission_classes = [IsAdminOrStoreManager]

    @swagger_auto_schema(
        operation_summary="Retrieve store schedule",
        operation_description="Retrieve a single store schedule",
        tags=["Appointments"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update store schedule",
        operation_description="Update a store schedule (Admin / Store Manager only)",
        tags=["Appointments"],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial update store schedule",
        operation_description="Partially update a store schedule (Admin / Store Manager only)",
        tags=["Appointments"],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


@swagger_auto_schema(
    method="get",
    operation_summary="Get available slots",
    operation_description="Get available appointment slots for a store and date",
    manual_parameters=[
        openapi.Parameter(
            "date",
            openapi.IN_QUERY,
            description="Target date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format="date",
            required=False,
        )
    ],
    responses={200: AvailableSlotSerializer(many=True)},
    tags=["Appointments"],
)
@api_view(["GET"])
def available_slots(request, store_id):
    """
    Get available slots for a given store and date
    GET param: ?date=YYYY-MM-DD
    """
    target_date = request.GET.get("date")
    if not target_date:
        target_date = date.today()
    else:
        target_date = date.fromisoformat(target_date)

    from store.models import Store

    try:
        store = Store.objects.get(id=store_id)
    except Store.DoesNotExist:
        return Response({"error": "Store not found"}, status=404)

    slots = generate_available_slots(store, target_date)
    serializer = AvailableSlotSerializer(slots, many=True)
    return Response(serializer.data)


class AppointmentCreateView(generics.CreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Create appointment",
        operation_description="Book an appointment by selecting an available slot",
        tags=["Appointments"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        store = serializer.validated_data["store"]
        target_date = serializer.validated_data["date"]

        requested_start_time = serializer.validated_data.get("start_time", None)
        available_slots = generate_available_slots(store, target_date)

        if not available_slots:
            raise serializers.ValidationError("No available slots for this date")

        if requested_start_time:
            requested_start_time = requested_start_time.replace(second=0, microsecond=0)

            slot = next(
                (s for s in available_slots if s["start_time"] == requested_start_time),
                None,
            )

            if not slot:
                raise serializers.ValidationError("Selected slot is not available")

        else:
            slot = available_slots[0]

        serializer.save(
            start_time=slot["start_time"],
            end_time=slot["end_time"],
            serial_no=slot["serial_no"],
        )


class AppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List appointments",
        operation_description="List appointments based on user role",
        tags=["Appointments"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.role == "SUPER_ADMIN":
            return Appointment.objects.select_related("store").all()
        elif user.role in ["STORE_MANAGER", "STAFF"]:
            return Appointment.objects.select_related("store").filter(store=user.store)
        else:
            return Appointment.objects.none()
