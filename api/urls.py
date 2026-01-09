from django.urls import path, include

urlpatterns = [
    path("services/", include("price_list.urls")),
    path("", include("store.urls")),
    path("", include("ai_behavior.urls")),
    path("", include("ai_api_key.urls")),
    path("call/", include("callLogs.urls")),
    path("call-transfer/", include("call_transfer.urls")),
]
