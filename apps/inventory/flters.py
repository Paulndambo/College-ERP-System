
import django_filters

from apps.inventory.models import InventoryItem


class InventoryItemFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name="category_id")
    category_type = django_filters.CharFilter(field_name="category__category_type")

    class Meta:
        model = InventoryItem
        fields = ["category", "category_type"]
