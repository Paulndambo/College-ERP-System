import django_filters
from django.db.models import Q

from .models import Transaction


class TransactionFilter(django_filters.FilterSet):
    account = django_filters.NumberFilter(field_name="account__id", label="Account ID")
    reference = django_filters.CharFilter(
        field_name="journal__reference", lookup_expr="icontains", label="Reference"
    )
    is_debit = django_filters.BooleanFilter(field_name="is_debit", label="Is Debit")

    class Meta:
        model = Transaction
        fields = ["account", "reference", "is_debit"]
