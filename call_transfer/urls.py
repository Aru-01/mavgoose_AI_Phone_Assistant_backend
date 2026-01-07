from rest_framework.routers import DefaultRouter
from .views import (
    TransferConditionViewSet,
    TransferContactViewSet,
    StoreTransferRuleViewSet,
)

router = DefaultRouter()
router.register("conditions", TransferConditionViewSet)
router.register("contacts", TransferContactViewSet)
router.register("rules", StoreTransferRuleViewSet)

urlpatterns = router.urls
