import django_filters
from .models import (
   
    PurchaseOrder,
    Vendor,
)


class VendorFilter(django_filters.FilterSet):
    vendor_no = django_filters.CharFilter(lookup_expr="icontains")


    class Meta:
        model = Vendor
        fields = ["vendor_no",]
class OrderFilter(django_filters.FilterSet):
    order_no = django_filters.CharFilter(lookup_expr="icontains")


    class Meta:
        model = PurchaseOrder
        fields = ["order_no",]
