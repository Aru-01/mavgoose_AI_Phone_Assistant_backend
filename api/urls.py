from rest_framework.routers import DefaultRouter
from price_list.views import (
    CategoryViewSet,
    BrandViewSet,
    DeviceModelViewSet,
    RepairTypeViewSet,
    PriceListViewSet,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("brands", BrandViewSet)
router.register("device-models", DeviceModelViewSet)
router.register("repair-types", RepairTypeViewSet)
router.register("price-list", PriceListViewSet)

urlpatterns = router.urls
