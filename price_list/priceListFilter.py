import django_filters
from price_list.models import PriceList


class PriceListFilter(django_filters.FilterSet):
    class Meta:
        model = PriceList
        fields = {
            "category": ["exact"],
            "brand": ["exact"],
            "device_model": ["exact"],
            "repair_type": ["exact"],
            "status": ["exact"],
        }


class PriceListAdminFilter(PriceListFilter):
    class Meta(PriceListFilter.Meta):
        fields = {
            **PriceListFilter.Meta.fields,
            "store": ["exact"],
        }