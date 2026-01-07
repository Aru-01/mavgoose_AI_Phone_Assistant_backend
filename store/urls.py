from rest_framework.routers import DefaultRouter
from store.views import StoreViewSet

router = DefaultRouter()
router.register("stores", StoreViewSet, basename="store")

urlpatterns = router.urls
