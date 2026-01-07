from rest_framework import serializers
from price_list.models import Category, Brand, DeviceModel, RepairType, PriceList


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
        ]


class BrandSerializer(serializers.ModelSerializer):
    category_name = serializers.StringRelatedField(source="category", read_only=True)

    class Meta:
        model = Brand
        fields = ["id", "name", "category", "category_name"]

    def validate(self, attrs):
        if Brand.objects.filter(
            name=attrs["name"], category=attrs["category"]
        ).exists():
            raise serializers.ValidationError(
                "This brand already exists for this category."
            )
        return attrs


class DeviceModelSerializer(serializers.ModelSerializer):
    brand = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.select_related("category").all()
    )
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    category_name = serializers.CharField(source="brand.category.name", read_only=True)

    class Meta:
        model = DeviceModel
        fields = ["id", "name", "brand", "brand_name", "category_name"]


class RepairTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairType
        fields = ["id", "name"]


class PriceListReadSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")
    brand_name = serializers.ReadOnlyField(source="brand.name")
    device_model_name = serializers.ReadOnlyField(source="device_model.name")
    repair_type_name = serializers.ReadOnlyField(source="repair_type.name")

    class Meta:
        model = PriceList
        fields = [
            "id",
            "category_name",
            "store",
            "brand_name",
            "device_model_name",
            "repair_type_name",
            "price",
            "status",
            "updated_at",
        ]


class PriceListWriteSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    brand = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.select_related("category").all()
    )
    device_model = serializers.PrimaryKeyRelatedField(
        queryset=DeviceModel.objects.select_related("brand", "brand__category").all()
    )
    repair_type = serializers.PrimaryKeyRelatedField(queryset=RepairType.objects.all())

    class Meta:
        model = PriceList
        fields = [
            "id",
            "category",
            "store",
            "brand",
            "device_model",
            "repair_type",
            "price",
            "status",
        ]
