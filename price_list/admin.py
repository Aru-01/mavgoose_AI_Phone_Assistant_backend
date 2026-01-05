from django.contrib import admin
from price_list.models import Category, Brand, RepairType, PriceList, DeviceModel

# Register your models here.
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(RepairType)
admin.site.register(DeviceModel)
admin.site.register(PriceList)
