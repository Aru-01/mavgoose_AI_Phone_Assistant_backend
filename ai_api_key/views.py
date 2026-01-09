from rest_framework import viewsets
from rest_framework.response import Response
from ai_api_key.models import APIKey, Speech_to_Text, Model_Configuration
from ai_api_key.serializers import (
    Model_Configuration_Serializer,
    STTConfigSerializer,
    APIKeySerializer,
)
from store.models import Store
from api.permissions import IsAdminUserRole
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


AI_CONFIG_REQUEST_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "ai_config": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description="Model configuration settings",
        ),
        "stt_config": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description="Speech-to-text configuration",
        ),
        "api_key": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description="API key configuration",
        ),
    },
)

AI_CONFIG_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "ai_config": openapi.Schema(type=openapi.TYPE_OBJECT),
        "stt_config": openapi.Schema(type=openapi.TYPE_OBJECT),
        "api_key": openapi.Schema(type=openapi.TYPE_OBJECT),
    },
)


class StoreAIConfigViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUserRole]

    def _get_store(self, store_id):
        return Store.objects.filter(id=store_id).first()

    @swagger_auto_schema(
        operation_summary="Retrieve AI settings for a store",
        operation_description="""
        Retrieve all AI related configurations for a store.

        **Includes:**
        - AI model configuration
        - Speech-to-text configuration
        - Active API key

        **Access:** Super Admin only
        """,
        responses={
            200: openapi.Response(
                description="AI configuration retrieved",
                schema=AI_CONFIG_RESPONSE_SCHEMA,
            ),
            404: "Store not found",
            401: "Unauthorized",
            403: "Forbidden",
        },
        tags=["AI Api settings {Only for Super Admin}"],
    )
    def retrieve(self, request, store_id=None):
        store = self._get_store(store_id)
        if not store:
            return Response({"detail": "Store not found"}, status=404)

        ai_config = Model_Configuration.objects.filter(store=store).first()
        stt_config = Speech_to_Text.objects.filter(store=store).first()
        api_key = (
            APIKey.objects.filter(store=store, active=True)
            .order_by("-created_at")
            .first()
        )

        return Response(
            {
                "ai_config": (
                    Model_Configuration_Serializer(ai_config).data if ai_config else {}
                ),
                "stt_config": (
                    STTConfigSerializer(stt_config).data if stt_config else {}
                ),
                "api_key": APIKeySerializer(api_key).data if api_key else {},
            }
        )

    @swagger_auto_schema(
        operation_summary="Create AI configuration for a store",
        operation_description="""
        Create AI, STT and API key configuration for a store.

        ⚠️ Only one configuration allowed per store.
        """,
        request_body=AI_CONFIG_REQUEST_SCHEMA,
        responses={
            201: "Config created successfully",
            400: "Config already exists / Validation error",
            404: "Store not found",
            401: "Unauthorized",
            403: "Forbidden",
        },
        tags=["AI Api settings {Only for Super Admin}"],
    )
    def create(self, request, store_id=None):
        store = self._get_store(store_id)
        if not store:
            return Response({"detail": "Store not found"}, status=404)

        if Model_Configuration.objects.filter(store=store).exists():
            return Response(
                {"detail": "Config already exists. Use PATCH to update."}, status=400
            )

        # AIConfig
        ai_serializer = Model_Configuration_Serializer(
            data=request.data.get("ai_config", {})
        )
        ai_serializer.is_valid(raise_exception=True)
        ai_serializer.save(store=store)

        # STTConfig
        stt_serializer = STTConfigSerializer(data=request.data.get("stt_config", {}))
        stt_serializer.is_valid(raise_exception=True)
        stt_serializer.save(store=store)

        # APIKey
        api_data = request.data.get("api_key")
        if api_data:
            api_serializer = APIKeySerializer(
                data={**api_data, "store": store.id, "active": True}
            )
            api_serializer.is_valid(raise_exception=True)
            api_serializer.save()

        return Response({"detail": "Config created"}, status=201)

    @swagger_auto_schema(
        operation_summary="Update AI configuration for a store",
        operation_description="""
        Partial update of AI model, STT configuration, or rotate API key.

        - Partial updates supported
        - Old API key will be deleted automatically
        """,
        request_body=AI_CONFIG_REQUEST_SCHEMA,
        responses={
            200: "Config updated successfully",
            400: "Validation error",
            404: "Store not found",
            401: "Unauthorized",
            403: "Forbidden",
        },
        tags=["AI Api settings {Only for Super Admin}"],
    )
    def partial_update(self, request, store_id=None):
        store = self._get_store(store_id)
        if not store:
            return Response({"detail": "Store not found"}, status=404)

        # AI Config
        ai_config = Model_Configuration.objects.filter(store=store).first()
        if ai_config:
            ai_serializer = Model_Configuration_Serializer(
                ai_config, data=request.data.get("ai_config", {}), partial=True
            )
            ai_serializer.is_valid(raise_exception=True)
            ai_serializer.save()

        # STT Config
        stt_config = Speech_to_Text.objects.filter(store=store).first()
        if stt_config:
            stt_serializer = STTConfigSerializer(
                stt_config, data=request.data.get("stt_config", {}), partial=True
            )
            stt_serializer.is_valid(raise_exception=True)
            stt_serializer.save()

        # APIKey rotation (delete old, create new)
        api_data = request.data.get("api_key")
        if api_data:
            APIKey.objects.filter(store=store, active=True).delete()
            api_serializer = APIKeySerializer(
                data={**api_data, "store": store.id, "active": True}
            )
            api_serializer.is_valid(raise_exception=True)
            api_serializer.save()

        return Response({"detail": "Config updated"})
