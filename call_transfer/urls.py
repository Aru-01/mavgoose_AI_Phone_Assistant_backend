from rest_framework.routers import DefaultRouter
from .views import TransferConditionViewSet, TransferContactViewSet, CallTransferViewSet

router = DefaultRouter()
router.register("conditions", TransferConditionViewSet)
router.register("contacts", TransferContactViewSet)
router.register("", CallTransferViewSet)

urlpatterns = router.urls
