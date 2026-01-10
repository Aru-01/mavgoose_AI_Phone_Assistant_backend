from django.db import models
from django.core.exceptions import ValidationError
from store.models import Store
from price_list.models import RepairType, DeviceModel, Brand, Category
from datetime import datetime, timedelta


class StoreSchedule(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="schedules")

    day = models.PositiveSmallIntegerField(
        choices=[
            (0, "Monday"),
            (1, "Tuesday"),
            (2, "Wednesday"),
            (3, "Thursday"),
            (4, "Friday"),
            (5, "Saturday"),
            (6, "Sunday"),
        ]
    )

    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)

    is_open = models.BooleanField(default=True)

    slots_per_hour = models.PositiveSmallIntegerField(default=2)
    max_slots_per_hour = 6

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("store", "day")

    def __str__(self):
        return f"{self.store.name} - {self.get_day_display()}"

    def slot_duration_minutes(self):
        if self.slots_per_hour > self.max_slots_per_hour:
            return 60 // self.max_slots_per_hour
        return 60 // self.slots_per_hour

    def clean(self):
        # Enforce max_slots_per_hour
        if self.slots_per_hour > self.max_slots_per_hour:
            raise ValidationError(
                f"slots_per_hour cannot exceed {self.max_slots_per_hour}"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Appointment(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="appointments"
    )

    client_name = models.CharField(max_length=200)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20)

    repair_type = models.ForeignKey(RepairType, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    device_model = models.ForeignKey(DeviceModel, on_delete=models.CASCADE)

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    serial_no = models.PositiveSmallIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("store", "date", "start_time")

    def __str__(self):
        return f"{self.client_name} - {self.store.name} - {self.date} {self.start_time}"


def generate_available_slots(store, target_date):
    schedule = store.schedules.filter(day=target_date.weekday(), is_open=True).first()

    if not schedule:
        return []

    duration = schedule.slot_duration_minutes()

    start_dt = datetime.combine(target_date, schedule.open_time)
    end_dt = datetime.combine(target_date, schedule.close_time)

    booked_slots = set(
        t.replace(second=0, microsecond=0)
        for t in store.appointments.filter(date=target_date).values_list(
            "start_time", flat=True
        )
    )

    available_slots = []
    current = start_dt

    while current + timedelta(minutes=duration) <= end_dt:
        slot_start = current.time().replace(second=0, microsecond=0)
        slot_end = (
            (current + timedelta(minutes=duration))
            .time()
            .replace(second=0, microsecond=0)
        )

        # ✅ absolute serial (time-based)
        minutes_from_open = int((current - start_dt).total_seconds() / 60)
        serial_no = (minutes_from_open // duration) + 1

        if slot_start not in booked_slots:
            available_slots.append(
                {
                    "start_time": slot_start,
                    "end_time": slot_end,
                    "serial_no": serial_no,
                }
            )

        current += timedelta(minutes=duration)

    return available_slots
