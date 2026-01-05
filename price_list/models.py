from django.db import models


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="brands"
    )

    class Meta:
        unique_together = ("name", "category")

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class DeviceModel(models.Model):
    name = models.CharField(max_length=150)
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name="device_models"
    )

    def __str__(self):
        return f"{self.brand.name} {self.name}"


class RepairType(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class ServiceStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    DISABLED = "DISABLED", "Disabled"


class PriceList(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="price_list_by_category"
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name="price_list_by_brand"
    )
    device_model = models.ForeignKey(
        DeviceModel, on_delete=models.CASCADE, related_name="price_list_by_model"
    )
    repair_type = models.ForeignKey(
        RepairType, on_delete=models.CASCADE, related_name="price_list_by_repair_type"
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20, choices=ServiceStatus.choices, default=ServiceStatus.ACTIVE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        unique_together = (
            "device_model",
            "repair_type",
        )

    def __str__(self):
        return f"{self.device_model} - {self.repair_type} (${self.price})"
