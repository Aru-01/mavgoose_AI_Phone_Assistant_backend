from django.urls import path
from rest_framework.routers import DefaultRouter
from callLogs.views import CallSessionViewSet,StoreCallSummaryView,CallTrendsView

router = DefaultRouter()
router.register("details", CallSessionViewSet, basename="call-logs")

urlpatterns = router.urls
urlpatterns+=[
    path("store-summary/", StoreCallSummaryView.as_view(), name="store-summary"),
    path("call-trends/", CallTrendsView.as_view(), name="call-trends"),
    ]