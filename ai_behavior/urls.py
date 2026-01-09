from django.urls import path
from ai_behavior.views import (
    AIConfigCreateView,
    AIConfigDetailView,
    AutoTransferKeywordDetailView,
    AutoTransferKeywordListCreateView,
)

urlpatterns = [
    # AI behavior
    path(
        "stores/<int:store_id>/ai-behavior/",
        AIConfigDetailView.as_view(),
        name="ai-behavior-detail",
    ),
    path(
        "stores/<int:store_id>/ai-behavior/create/",
        AIConfigCreateView.as_view(),
        name="ai-behavior-create",
    ),
    # Keywords (under store → ai-behavior)
    path(
        "stores/<int:store_id>/ai-behavior/keywords/",
        AutoTransferKeywordListCreateView.as_view(),
        name="keywords-list-create",
    ),
    path(
        "stores/<int:store_id>/ai-behavior/keywords/<int:pk>/",
        AutoTransferKeywordDetailView.as_view(),
        name="keywords-detail",
    ),
]
