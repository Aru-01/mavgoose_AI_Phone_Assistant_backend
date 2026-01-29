from rest_framework import mixins, viewsets, filters
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
from django.utils import timezone
from callLogs.models import CallSession
from accounts.models import UserRole
from callLogs.serializers import CallSessionSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from django.db.models.functions import TruncDay
from django.db.models import Count, Avg
from store.models import Store
import calendar


class CallSessionViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    API for Call Logs:
    - List all call sessions
    - Create new call session (AI POST)
    - PUT/PATCH/DELETE NOT allowed
    """

    queryset = (
        CallSession.objects.select_related("issue")
        .prefetch_related("transcripts")
        .all()
    )
    serializer_class = CallSessionSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["call_type", "issue"]
    search_fields = ["phone_number", "issue__name"]

    @swagger_auto_schema(
        operation_summary="List call sessions",
        operation_description=(
            "Retrieve a list of call sessions with optional filters.\n\n"
            "**Role-based filtering:**\n"
            "- Staff / Store Manager: Only see calls from their store.\n"
            "- Super Admin: Can see all calls, optionally filter by store using `store` query param."
        ),
        tags=["Call Logs"],
        manual_parameters=[
            openapi.Parameter(
                "date",
                openapi.IN_QUERY,
                description="Filter by date: today, this_week, this_month",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "call_type",
                openapi.IN_QUERY,
                description="Filter by call type",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "issue",
                openapi.IN_QUERY,
                description="Filter by issue ID",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search by phone number or issue name",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "store",
                openapi.IN_QUERY,
                description="Filter by store ID (only for Super Admin)",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create call session",
        operation_description="Create a new call session with transcripts",
        tags=["Call Logs"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve call session",
        operation_description="Get details of a single call session",
        tags=["Call Logs"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return CallSession.objects.none()

        qs = super().get_queryset()
        user = self.request.user

        if user.role in [UserRole.STAFF, UserRole.STORE_MANAGER]:
            qs = qs.filter(store=user.store)
        elif user.role == UserRole.SUPER_ADMIN:
            store_id = self.request.query_params.get("store")
            if store_id:
                qs = qs.filter(store_id=store_id)

        date_filter = self.request.query_params.get("date")
        now = timezone.now()

        if date_filter == "today":
            qs = qs.filter(created_at__date=now.date())
        elif date_filter == "this_week":
            start_week = now - timedelta(days=now.weekday())
            qs = qs.filter(created_at__date__gte=start_week.date())
        elif date_filter == "this_month":
            qs = qs.filter(created_at__year=now.year, created_at__month=now.month)

        return qs


class StoreCallSummaryView(APIView):
    """
    Store-wise call summary for today
    Role-based:
    - Staff / Store Manager: Only their store
    - Super Admin: All stores (optional filter by store_id)
    """

    @swagger_auto_schema(
        operation_summary="Store-wise Call Summary (Today)",
        operation_description=(
            "Retrieve call summary for today.\n\n"
            "Role-based:\n"
            "- Staff / Store Manager: Only their store\n"
            "- Super Admin: All stores (optional filter by `store_id` query param)"
        ),
        tags=["Dashboard"],
        manual_parameters=[
            openapi.Parameter(
                "store_id",
                openapi.IN_QUERY,
                description="Filter by store ID (only for Super Admin, optional)",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "store_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "store_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "total_calls_today": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "ai_handled": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "warm_transfer": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "appointments_booked": openapi.Schema(
                            type=openapi.TYPE_INTEGER
                        ),
                        "missed_calls": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "avg_call_duration": openapi.Schema(type=openapi.TYPE_NUMBER),
                    },
                ),
            )
        },
    )
    def get(self, request):
        today = timezone.now().date()
        user = request.user

        store_id = request.query_params.get("store_id")  # <-- query param

        if user.role in [UserRole.STAFF, UserRole.STORE_MANAGER]:
            # staff/store_manager: শুধু তাদের store
            stores = Store.objects.filter(id=user.store.id)
        else:
            # super admin
            if store_id:
                stores = Store.objects.filter(id=store_id)
            else:
                stores = Store.objects.all()

        data = []
        for store in stores:
            calls = CallSession.objects.filter(store=store, started_at__date=today)

            total_calls = calls.count()
            ai_handled = calls.filter(call_type="AI_RESOLVED").count()
            warm_transfer = calls.filter(call_type="WARM_TRANSFER").count()
            appointments = calls.filter(call_type="APPOINTMENT").count()
            missed_calls = calls.filter(
                call_type__in=["DROPPED", "CALL_DROPPED"]
            ).count()

            # avg duration in minutes
            durations = []
            for call in calls:
                if call.duration:
                    # assuming duration stored as "HH:MM:SS" or "MM:SS"
                    parts = [int(x) for x in call.duration.split(":")]
                    if len(parts) == 3:
                        sec = parts[0] * 3600 + parts[1] * 60 + parts[2]
                    elif len(parts) == 2:
                        sec = parts[0] * 60 + parts[1]
                    else:
                        sec = 0
                    durations.append(sec)
            avg_duration = sum(durations) / len(durations) / 60 if durations else 0

            data.append(
                {
                    "store_id": store.id,
                    "store_name": store.name,
                    "total_calls_today": total_calls,
                    "ai_handled": ai_handled,
                    "warm_transfer": warm_transfer,
                    "appointments_booked": appointments,
                    "missed_calls": missed_calls,
                    "avg_call_duration": round(avg_duration, 2),
                }
            )

        return Response(data)


class CallTrendsView(APIView):
    """
    Calls trend for this week (last 7 days)
    Role-based:
    - Staff / Store Manager: only their store
    - Super Admin: all stores, optionally filter by store query param
    """

    @swagger_auto_schema(
        operation_summary="Call Trends (Last 7 Days)",
        operation_description=(
            "Retrieve call trends for the last 7 days. Day-wise (Mon, Tue, ...) with total calls.\n\n"
            "Role-based:\n"
            "- Staff / Store Manager: Only their store\n"
            "- Super Admin: Can optionally filter by store using `store` query param"
        ),
        tags=["Dashboard"],
        manual_parameters=[
            openapi.Parameter(
                "store",
                openapi.IN_QUERY,
                description="Store ID to filter (Super Admin only)",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "total_calls": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "trend": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        additional_properties=openapi.Schema(type=openapi.TYPE_INTEGER),
                    ),
                },
            )
        },
    )
    def get(self, request):
        today = timezone.now().date()
        week_ago = today - timedelta(days=6)
        user = request.user

        # base queryset
        qs = CallSession.objects.filter(
            started_at__date__gte=week_ago,
            started_at__date__lte=today,
        )

        # role-based filter
        if user.role in [UserRole.STAFF, UserRole.STORE_MANAGER]:
            qs = qs.filter(store=user.store)
        elif user.role == UserRole.SUPER_ADMIN:
            store_id = request.query_params.get("store")
            if store_id:
                qs = qs.filter(store_id=store_id)

        # annotate day and count
        calls = (
            qs.annotate(day=TruncDay("started_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        # prepare day labels Mon, Tue, ...
        trend = {}
        for i in range(7):
            day = week_ago + timedelta(days=i)
            label = calendar.day_abbr[day.weekday()]  # Mon, Tue, ...
            trend[label] = 0

        for c in calls:
            label = calendar.day_abbr[c["day"].weekday()]
            trend[label] = c["count"]

        total_calls = sum(trend.values())

        return Response({"total_calls": total_calls, "trend": trend})
