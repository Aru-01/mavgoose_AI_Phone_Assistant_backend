from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AIConfig
from .serializers import (
    AIConfigSerializer,
    AutoTransferKeywordCRUDSerializer,
    AutoTransferKeyword,
)


###### --> Custom mixin ##########
class AIConfigMixin:
    def get_ai_config(self):
        if not hasattr(self, "_ai_config"):
            store_id = self.kwargs["store_id"]
            self._ai_config = get_object_or_404(
                AIConfig.objects.select_related("store"), store_id=store_id
            )
        return self._ai_config


###### --> Custom mixin ##########


def get_ai_config(self):
    store_id = self.kwargs["store_id"]
    return get_object_or_404(AIConfig, store_id=store_id)


class AutoTransferKeywordListCreateView(AIConfigMixin, generics.ListCreateAPIView):
    serializer_class = AutoTransferKeywordCRUDSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AutoTransferKeyword.objects.filter(ai_config=self.get_ai_config())

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["ai_config"] = self.get_ai_config()
        return context

    def perform_create(self, serializer):
        serializer.save(ai_config=self.get_ai_config())


class AutoTransferKeywordDetailView(
    AIConfigMixin, generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = AutoTransferKeywordCRUDSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["ai_config"] = self.get_ai_config()
        return context

    def get_queryset(self):
        return AutoTransferKeyword.objects.filter(ai_config=self.get_ai_config())


class AIConfigCreateView(generics.CreateAPIView):
    serializer_class = AIConfigSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        store_id = request.data.get("store")
        if AIConfig.objects.filter(store_id=store_id).exists():
            return Response(
                {
                    "detail": "AI config already exists for this store. You can only update it."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)


class AIConfigDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = AIConfigSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "store_id"

    def get_queryset(self):
        return (
            AIConfig.objects.select_related("store", "greetings")
            .prefetch_related(
                "business_hours",
                "auto_transfer_keywords",
            )
            .all()
        )
