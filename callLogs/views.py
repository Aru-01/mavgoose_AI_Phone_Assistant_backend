from rest_framework import mixins, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
from django.utils import timezone
from .models import CallSession
from .serializers import CallSessionSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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
        operation_description="Retrieve a list of call sessions with optional filters",
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
        qs = super().get_queryset()

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

