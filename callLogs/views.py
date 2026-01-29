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
    """
    def get(self, request):
        today = timezone.now().date()
        stores = Store.objects.all()
        data = []

        for store in stores:
            calls = CallSession.objects.filter(
                store=store,
                started_at__date=today
            )

            total_calls = calls.count()
            ai_handled = calls.filter(call_type="AI_RESOLVED").count()
            warm_transfer = calls.filter(call_type="WARM_TRANSFER").count()
            appointments = calls.filter(call_type="APPOINTMENT").count()
            missed_calls = calls.filter(call_type__in=["DROPPED", "CALL_DROPPED"]).count()

            # avg duration in minutes
            durations = []
            for call in calls:
                if call.duration:
                    # assuming duration stored as "HH:MM:SS" or "MM:SS"
                    parts = [int(x) for x in call.duration.split(":")]
                    if len(parts) == 3:
                        sec = parts[0]*3600 + parts[1]*60 + parts[2]
                    elif len(parts) == 2:
                        sec = parts[0]*60 + parts[1]
                    else:
                        sec = 0
                    durations.append(sec)
            avg_duration = sum(durations)/len(durations)/60 if durations else 0

            data.append({
                "store_id": store.id,
                "store_name": store.name,
                "total_calls_today": total_calls,
                "ai_handled": ai_handled,
                "warm_transfer": warm_transfer,
                "appointments_booked": appointments,
                "missed_calls": missed_calls,
                "avg_call_duration": round(avg_duration, 2)
            })

        return Response(data)
    


class CallTrendsView(APIView):
    """
    Calls trend for this week (last 7 days)
    """
    def get(self, request):
        today = timezone.now().date()
        week_ago = today - timedelta(days=6)

        calls = CallSession.objects.filter(
            started_at__date__gte=week_ago,
            started_at__date__lte=today
        ).annotate(day=TruncDay('started_at')).values('day').annotate(count=Count('id')).order_by('day')

        # convert to dict with all 7 days
        trend = {}
        for i in range(7):
            day = week_ago + timedelta(days=i)
            trend[day.strftime("%Y-%m-%d")] = 0

        for c in calls:
            trend[c['day'].strftime("%Y-%m-%d")] = c['count']

        total_calls = sum(trend.values())

        return Response({
            "total_calls": total_calls,
            "trend": trend
        })