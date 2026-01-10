from rest_framework import viewsets
from django.db.models import F
from price_list.models import Category, Brand, PriceList, RepairType, DeviceModel
from price_list import serializers as sz
from accounts.models import UserRole
from drf_yasg.utils import swagger_auto_schema


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Category API:
    - List / Retrieve / Create / Update / Delete categories
    """

    queryset = Category.objects.all()
    serializer_class = sz.CategorySerializer

    @swagger_auto_schema(
        operation_summary="List all categories",
        operation_description="Retrieve all categories.",
        responses={200: sz.CategorySerializer(many=True)},
        tags=["Price List (Category)"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a category",
        operation_description="Retrieve category by ID.",
        responses={200: sz.CategorySerializer()},
        tags=["Price List (Category)"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a category",
        operation_description="Create a new category.",
        request_body=sz.CategorySerializer,
        responses={201: sz.CategorySerializer()},
        tags=["Price List (Category)"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a category",
        operation_description="Update a category.",
        request_body=sz.CategorySerializer,
        responses={200: sz.CategorySerializer()},
        tags=["Price List (Category)"],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial update a category",
        operation_description="Partial update a category.",
        request_body=sz.CategorySerializer,
        responses={200: sz.CategorySerializer()},
        tags=["Price List (Category)"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a category",
        operation_description="Delete a category.",
        request_body=sz.CategorySerializer,
        responses={204: sz.CategorySerializer()},
        tags=["Price List (Category)"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class BrandViewSet(viewsets.ModelViewSet):
    """
    Brand API:
    - List / Retrieve / Create / Update / Delete brands
    """

    queryset = Brand.objects.select_related("category").all()
    serializer_class = sz.BrandSerializer

    @swagger_auto_schema(
        operation_summary="List all brands",
        operation_description="Retrieve all brands.",
        responses={200: sz.BrandSerializer(many=True)},
        tags=["Price List (Brand)"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a Brand",
        operation_description="Retrieve Brand by ID.",
        responses={200: sz.BrandSerializer()},
        tags=["Price List (Brand)"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a Brand",
        operation_description="Create a new Brand.",
        request_body=sz.BrandSerializer,
        responses={201: sz.BrandSerializer()},
        tags=["Price List (Brand)"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a Brand",
        operation_description="Update a Brand.",
        request_body=sz.BrandSerializer,
        responses={200: sz.BrandSerializer()},
        tags=["Price List (Brand)"],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial update a Brand",
        operation_description="Partial update a Brand.",
        request_body=sz.BrandSerializer,
        responses={200: sz.BrandSerializer()},
        tags=["Price List (Brand)"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a Brand",
        operation_description="Delete a Brand.",
        request_body=sz.BrandSerializer,
        responses={204: sz.BrandSerializer()},
        tags=["Price List (Brand)"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class DeviceModelViewSet(viewsets.ModelViewSet):
    """
    Device Model API:
    - List / Retrieve / Create / Update / Delete device models
    """

    queryset = DeviceModel.objects.select_related("brand", "brand__category").all()
    serializer_class = sz.DeviceModelSerializer

    @swagger_auto_schema(
        operation_summary="List all Device Models",
        operation_description="Retrieve all Device Models.",
        responses={200: sz.DeviceModelSerializer(many=True)},
        tags=["Price List (Device Models)"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a Device Model",
        operation_description="Retrieve Device Model by ID.",
        responses={200: sz.DeviceModelSerializer()},
        tags=["Price List (Device Models)"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a Device Model",
        operation_description="Create a new Device Model.",
        request_body=sz.DeviceModelSerializer,
        responses={201: sz.DeviceModelSerializer()},
        tags=["Price List (Device Models)"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a Device Model",
        operation_description="Update a Device Model.",
        request_body=sz.DeviceModelSerializer,
        responses={200: sz.DeviceModelSerializer()},
        tags=["Price List (Device Models)"],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial update a Device Model",
        operation_description="Partial update a Device Model.",
        request_body=sz.DeviceModelSerializer,
        responses={200: sz.DeviceModelSerializer()},
        tags=["Price List (Device Models)"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a Device Model",
        operation_description="Delete a Device Model.",
        request_body=sz.DeviceModelSerializer,
        responses={204: sz.DeviceModelSerializer()},
        tags=["Price List (Device Models)"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class RepairTypeViewSet(viewsets.ModelViewSet):
    """
    Repair Type API:
    - List / Retrieve / Create / Update / Delete repair types
    """

    queryset = RepairType.objects.all()
    serializer_class = sz.RepairTypeSerializer

    @swagger_auto_schema(
        operation_summary="List all Repair Types",
        operation_description="Retrieve all Repair Types.",
        responses={200: sz.RepairTypeSerializer(many=True)},
        tags=["Price List (Repair Type)"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve a Repair Type",
        operation_description="Retrieve Repair Type by ID.",
        responses={200: sz.RepairTypeSerializer()},
        tags=["Price List (Repair Type)"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a Repair Type",
        operation_description="Create a new Repair Type.",
        request_body=sz.RepairTypeSerializer,
        responses={201: sz.RepairTypeSerializer()},
        tags=["Price List (Repair Type)"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a Repair Type",
        operation_description="Update a Repair Type.",
        request_body=sz.RepairTypeSerializer,
        responses={200: sz.RepairTypeSerializer()},
        tags=["Price List (Repair Type)"],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial update a Repair Type",
        operation_description="Partial update a Repair Type.",
        request_body=sz.RepairTypeSerializer,
        responses={200: sz.RepairTypeSerializer()},
        tags=["Price List (Repair Type)"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a Repair Type",
        operation_description="Delete a Repair Type.",
        request_body=sz.RepairTypeSerializer,
        responses={204: sz.RepairTypeSerializer()},
        tags=["Price List (Repair Type)"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class PriceListViewSet(viewsets.ModelViewSet):
    """
    Price List API:
    - List / Retrieve price list entries (read)
    - Create / Update / Delete price list entries (write)
    """

    # queryset = PriceList.objects.select_related(
    #     "category", "brand", "device_model", "device_model__brand", "repair_type"
    # )

    def get_queryset(self):
        user = self.request.user

        if user.role != UserRole.SUPER_ADMIN:
            return PriceList.objects.select_related(
                "category", "brand", "device_model", "repair_type"
            ).filter(store=user.store_id)

        # store manager / staff
        return PriceList.objects.select_related(
            "category", "brand", "device_model", "repair_type"
        )

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return sz.PriceListReadSerializer
        return sz.PriceListWriteSerializer

    @swagger_auto_schema(
        operation_summary="List price list entries",
        responses={200: sz.PriceListReadSerializer(many=True)},
        tags=["Price List"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve price list entry",
        responses={200: sz.PriceListReadSerializer()},
        tags=["Price List"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create price list entry",
        request_body=sz.PriceListWriteSerializer,
        responses={201: sz.PriceListWriteSerializer()},
        tags=["Price List"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update price list entry",
        request_body=sz.PriceListWriteSerializer,
        responses={200: sz.PriceListWriteSerializer()},
        tags=["Price List"],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial update price list entry",
        request_body=sz.PriceListWriteSerializer,
        responses={200: sz.PriceListWriteSerializer()},
        tags=["Price List"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete price list entry",
        responses={204: "No Content"},
        tags=["Price List"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
