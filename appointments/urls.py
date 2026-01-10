from django.urls import path
from .views import (
    StoreScheduleListCreateView,
    StoreScheduleRetrieveUpdateView,
    available_slots,
    AppointmentCreateView,
    AppointmentListView,
)

urlpatterns = [
    path("", AppointmentListView.as_view(), name="appointments-list"),
    path(
        "store-schedules/",
        StoreScheduleListCreateView.as_view(),
        name="store-schedule-list-create",
    ),
    path(
        "store-schedules/<int:pk>/",
        StoreScheduleRetrieveUpdateView.as_view(),
        name="store-schedule-retrieve-update",
    ),
    # ------------------------
    # Available Slots (Client)
    # ------------------------
    path(
        "stores/<int:store_id>/available-slots/",
        available_slots,
        name="available-slots",
    ),
    # ------------------------
    # Client Appointment Booking
    # ------------------------
    path(
        "book/",
        AppointmentCreateView.as_view(),
        name="appointment-book",
    ),
]
