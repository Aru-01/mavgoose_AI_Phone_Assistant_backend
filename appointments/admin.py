from django.contrib import admin
from appointments.models import StoreSchedule, Appointment

# Register your models here.
admin.site.register(StoreSchedule)
admin.site.register(Appointment)
