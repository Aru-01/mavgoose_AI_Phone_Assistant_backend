from rest_framework import viewsets
from django.db.models import F
from price_list.models import Category, Brand, PriceList, RepairType, DeviceModel
from price_list.serializers import (
    CategorySerializer,
    BrandSerializer,
    RepairTypeSerializer,
    PriceListReadSerializer,
    PriceListWriteSerializer,
    DeviceModelSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.select_related("category").all()
    serializer_class = BrandSerializer


class DeviceModelViewSet(viewsets.ModelViewSet):
    queryset = DeviceModel.objects.select_related("brand", "brand__category").all()
    serializer_class = DeviceModelSerializer


class RepairTypeViewSet(viewsets.ModelViewSet):
    queryset = RepairType.objects.all()
    serializer_class = RepairTypeSerializer


class PriceListViewSet(viewsets.ModelViewSet):
    queryset = PriceList.objects.select_related(
        "category", "brand", "device_model", "device_model__brand", "repair_type"
    )

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return PriceListReadSerializer
        return PriceListWriteSerializer
