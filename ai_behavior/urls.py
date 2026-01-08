from django.urls import path
from ai_behavior.views import (
    AIConfigCreateView,
    AIConfigDetailView,
    AutoTransferKeywordDetailView,
    AutoTransferKeywordListCreateView,
)

urlpatterns = [
    # AI Config
    path(
        "stores/<int:store_id>/ai-config/",
        AIConfigDetailView.as_view(),
        name="ai-config-detail",
    ),
    path(
        "stores/<int:store_id>/ai-config/create/",
        AIConfigCreateView.as_view(),
        name="ai-config-create",
    ),
    # Keywords (under store → ai-config)
    path(
        "stores/<int:store_id>/ai-config/keywords/",
        AutoTransferKeywordListCreateView.as_view(),
        name="keywords-list-create",
    ),
    path(
        "stores/<int:store_id>/ai-config/keywords/<int:pk>/",
        AutoTransferKeywordDetailView.as_view(),
        name="keywords-detail",
    ),
]
