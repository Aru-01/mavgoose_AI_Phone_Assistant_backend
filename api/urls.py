from django.urls import path, include

urlpatterns = [
    path("services/", include("price_list.urls")),
    path("call/", include("callLogs.urls")),
]
