from rest_framework.routers import DefaultRouter
from callLogs.views import CallSessionViewSet

router = DefaultRouter()
router.register("details", CallSessionViewSet, basename="call-logs")

urlpatterns = router.urls
