from rest_framework import serializers
from appointments.models import StoreSchedule, Appointment


class StoreScheduleSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source="store.name", read_only=True)
    open_time = serializers.TimeField(required=True)
    close_time = serializers.TimeField(required=True)
    slots_per_hour = serializers.IntegerField(required=True, min_value=1, max_value=6)

    class Meta:
        model = StoreSchedule
        fields = [
            "id",
            "store",
            "store_name",
            "day",
            "open_time",
            "close_time",
            "is_open",
            "slots_per_hour",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, data):
        open_time = data.get("open_time")
        close_time = data.get("close_time")
        if open_time and close_time and open_time >= close_time:
            raise serializers.ValidationError("open_time must be before close_time")

        # Optional: store manager cannot assign other store
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and user.role == "STORE_MANAGER":
            data["store"] = user.store  # force save to manager's store
        return data


class AppointmentSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source="store.name", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "store",
            "store_name",
            "client_name",
            "client_email",
            "client_phone",
            "repair_type",
            "category",
            "brand",
            "device_model",
            "date",
            "start_time",
            "end_time",
            "serial_no",
            "created_at",
        ]
        read_only_fields = ["serial_no", "end_time", "created_at"]


class AvailableSlotSerializer(serializers.Serializer):
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    serial_no = serializers.IntegerField()
