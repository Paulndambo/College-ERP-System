import django_filters
from django.db.models import Q
from .models import StockIssue

class StockIssueFilter(django_filters.FilterSet):

    department = django_filters.NumberFilter(field_name="issued_to_id", lookup_expr="exact")

    search = django_filters.CharFilter(method="filter_by_all", label="Search")

    class Meta:
        model = StockIssue
        fields = ["department", "search"]

    def filter_by_all(self, queryset, name, value):
        return queryset.filter(
            Q(inventory_item__name__icontains=value) |
            Q(inventory_item__category__name__icontains=value) |
            Q(remarks__icontains=value)
        )
