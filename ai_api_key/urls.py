from django.urls import path
from ai_api_key.views import StoreAIConfigViewSet

store_ai_config = StoreAIConfigViewSet.as_view(
    {
        "get": "retrieve",
        "post": "create",
        "patch": "partial_update",
    }
)

urlpatterns = [
    path(
        "stores/<int:store_id>/api-config/",
        store_ai_config,
        name="store-ai-config",
    ),
]
