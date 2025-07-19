from .models import StudentFeeInvoice, StudentFeeLedger, StudentFeePayment
import django_filters
from django.db.models import Q
from decimal import Decimal


class StudentFeeInvoiceFilter(django_filters.FilterSet):
    """
    Filter student fee invoices
    """

    search = django_filters.CharFilter(method="filter_by_all", label="Search")
    status = django_filters.CharFilter(field_name="status", lookup_expr="icontains")
    semester = django_filters.NumberFilter(field_name="semester_id")
    has_balance = django_filters.BooleanFilter(method="filter_by_balance")
    department = django_filters.NumberFilter(
        field_name="student__programme__department_id"
    )
    cohort = django_filters.NumberFilter(field_name="student__cohort_id")

    class Meta:
        model = StudentFeeInvoice
        fields = ["search", "status", "semester", "has_balance", "department", "cohort"]

    def filter_by_all(self, queryset, name, value):
        """
        Filter invoices by student registration number, student name, or reference
        """
        value = value.strip()
        return queryset.filter(
            Q(student__registration_number__icontains=value)
            | Q(student__user__first_name__icontains=value)
            | Q(student__user__last_name__icontains=value)
            | Q(reference__icontains=value)
        )

    def filter_by_balance(self, queryset, name, value):
        """
        Filter invoices that have outstanding balance (True) or are fully paid (False)
        """
        if value is True:
            # Has outstanding balance (amount > amount_paid)
            return queryset.extra(where=["amount > amount_paid"])
        elif value is False:
            return queryset.extra(where=["amount = amount_paid"])
        return queryset


class StudentFeePaymentFilter(django_filters.FilterSet):
    """
    Filter student fee invoices
    """

    search = django_filters.CharFilter(method="filter_by_all", label="Search")
    status = django_filters.CharFilter(field_name="status", lookup_expr="icontains")
    semester = django_filters.NumberFilter(field_name="semester_id")
    department = django_filters.NumberFilter(
        field_name="student__programme__department_id"
    )
    cohort = django_filters.NumberFilter(field_name="student__cohort_id")
    payment_method = django_filters.CharFilter(
        field_name="payment_method", lookup_expr="icontains"
    )

    class Meta:
        model = StudentFeePayment
        fields = [
            "search",
            "status",
            "semester",
            "department",
            "cohort",
            "payment_method",
        ]

    def filter_by_all(self, queryset, name, value):
        """
        Filter invoices by student registration number, student name, or reference
        """
        value = value.strip()
        return queryset.filter(
            Q(student__registration_number__icontains=value)
            | Q(student__user__first_name__icontains=value)
            | Q(student__user__last_name__icontains=value)
        )


class StudentFeeLedgerFilter(django_filters.FilterSet):
    """
    Filter student fee invoices
    """

    search = django_filters.CharFilter(method="filter_by_all", label="Search")
    status = django_filters.CharFilter(field_name="status", lookup_expr="icontains")
    semester = django_filters.NumberFilter(field_name="semester_id")
    department = django_filters.NumberFilter(
        field_name="student__programme__department_id"
    )
    cohort = django_filters.NumberFilter(field_name="student__cohort_id")

    class Meta:
        model = StudentFeeLedger
        fields = ["search", "status", "semester", "department", "cohort"]

    def filter_by_all(self, queryset, name, value):
        """
        Filter invoices by student registration number, student name, or reference
        """
        value = value.strip()
        return queryset.filter(
            Q(student__registration_number__icontains=value)
            | Q(student__user__first_name__icontains=value)
            | Q(student__user__last_name__icontains=value)
        )
