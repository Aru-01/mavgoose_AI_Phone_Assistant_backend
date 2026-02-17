from django.shortcuts import get_object_or_404
from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from ai_behavior.models import AIBehaviorConfig
from ai_behavior.serializers import (
    AIBehaviorConfigSerializer,
    AutoTransferKeywordCRUDSerializer,
    AutoTransferKeyword,
)
from api.permissions import AIBehaviorPermission
from drf_yasg.utils import swagger_auto_schema
import threading
from ai_behavior.services.ai_system_trigger import trigger_ai_system_update


###### --> Custom mixin ##########
class AIBehaviorConfigMixin:
    def get_ai_behavior_config(self):
        if getattr(self, "swagger_fake_view", False):
            return None

        if not hasattr(self, "_ai_behavior_config"):
            store_id = self.kwargs.get("store_id")
            if not store_id:
                return None

            self._ai_behavior_config = get_object_or_404(
                AIBehaviorConfig.objects.select_related("store"),
                store_id=store_id,
            )
        return self._ai_behavior_config


###### --> Custom mixin ##########


class AutoTransferKeywordListCreateView(
    AIBehaviorConfigMixin, generics.ListCreateAPIView
):
    serializer_class = AutoTransferKeywordCRUDSerializer
    permission_classes = [IsAuthenticated, AIBehaviorPermission]

    @swagger_auto_schema(
        operation_summary="List auto transfer keywords",
        operation_description="List auto transfer keywords for a store AI config",
        tags=["AI Behavior"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create auto transfer keyword",
        operation_description="Create a new auto transfer keyword for a store AI config",
        tags=["AI Behavior"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        ai_behavior_config = self.get_ai_behavior_config()
        if not ai_behavior_config:
            return AutoTransferKeyword.objects.none()
        return AutoTransferKeyword.objects.filter(ai_behavior_config=ai_behavior_config)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        ai_behavior_config = self.get_ai_behavior_config()
        if ai_behavior_config:
            context["ai_behavior_config"] = ai_behavior_config
        return context

    def perform_create(self, serializer):
        ai_behavior_config = self.get_ai_behavior_config()
        if not ai_behavior_config:
            raise serializers.ValidationError("Invalid store or AI config not found.")
        serializer.save(ai_behavior_config=ai_behavior_config)
        threading.Thread(target=trigger_ai_system_update).start()


class AutoTransferKeywordDetailView(
    AIBehaviorConfigMixin, generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = AutoTransferKeywordCRUDSerializer
    permission_classes = [IsAuthenticated, AIBehaviorPermission]

    @swagger_auto_schema(
        operation_summary="Retrieve auto transfer keyword",
        operation_description="Retrieve a single auto transfer keyword",
        tags=["AI Behavior"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update auto transfer keyword",
        operation_description="Update an auto transfer keyword",
        tags=["AI Behavior"],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial update auto transfer keyword",
        operation_description="Partially update an auto transfer keyword",
        tags=["AI Behavior"],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete auto transfer keyword",
        operation_description="Delete an auto transfer keyword",
        tags=["AI Behavior"],
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        ai_behavior_config = self.get_ai_behavior_config()
        if ai_behavior_config:
            context["ai_behavior_config"] = ai_behavior_config
        return context

    def get_queryset(self):
        ai_behavior_config = self.get_ai_behavior_config()
        if not ai_behavior_config:
            return AutoTransferKeyword.objects.none()
        return AutoTransferKeyword.objects.filter(ai_behavior_config=ai_behavior_config)

    def perform_destroy(self, instance):
        instance.delete()
        threading.Thread(target=trigger_ai_system_update).start()


class AIBehaviorConfigCreateView(generics.CreateAPIView):
    serializer_class = AIBehaviorConfigSerializer
    permission_classes = [IsAuthenticated, AIBehaviorPermission]

    def get_queryset(self):
        return AIBehaviorConfig.objects.all()

    @swagger_auto_schema(
        operation_summary="Create AI configuration",
        operation_description="Create AI configuration for a store (one per store)",
        tags=["AI Behavior"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        store_id = self.kwargs.get("store_id")

        if AIBehaviorConfig.objects.filter(store_id=store_id).exists():
            raise serializers.ValidationError(
                "AI config already exists for this store. You can only update it."
            )

        serializer.save(store_id=store_id)
        threading.Thread(target=trigger_ai_system_update).start()


class AIBehaviorConfigDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = AIBehaviorConfigSerializer
    permission_classes = [IsAuthenticated, AIBehaviorPermission]
    lookup_field = "store_id"

    @swagger_auto_schema(
        operation_summary="Retrieve AI configuration",
        operation_description="Retrieve AI configuration by store ID",
        tags=["AI Behavior"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update AI configuration",
        operation_description="Update AI configuration including greetings, business hours and keywords",
        tags=["AI Behavior"],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial update AI configuration",
        operation_description="Partially update AI configuration",
        tags=["AI Behavior"],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            AIBehaviorConfig.objects.select_related("store", "greetings")
            .prefetch_related(
                "business_hours",
                "auto_transfer_keywords",
            )
            .all()
        )

    def perform_update(self, serializer):
        serializer.save()
        threading.Thread(target=trigger_ai_system_update).start()
