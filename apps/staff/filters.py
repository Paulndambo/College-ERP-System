from .models import Payslip, Staff, StaffLeave, StaffLeaveApplication, StaffPayroll
import django_filters

from apps.schools.models import Course, Programme, Semester, Department
from django.db.models import Count, Q


class StaffFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(method="filter_by_all", label="Search")
    status = django_filters.CharFilter(field_name="status", lookup_expr="icontains")
    department = django_filters.NumberFilter(field_name="department_id")

    class Meta:
        model = Staff
        fields = ["search", "status", "department"]

    def filter_by_all(self, queryset, name, value):
        """
        Filter staff by all fields
        """
        return queryset.filter(
            Q(staff_number__icontains=value) | Q(user__phone_number__icontains=value)
        )


class PayrollFilter(django_filters.FilterSet):
    """
    Filter staff payroll
    """

    search = django_filters.CharFilter(method="filter_by_all", label="Search")
    status = django_filters.CharFilter(field_name="status", lookup_expr="icontains")
    department = django_filters.NumberFilter(field_name="staff__department_id")

    class Meta:
        model = StaffPayroll
        fields = ["status", "department", "search"]

    def filter_by_all(self, queryset, name, value):
        value = value.strip()
        return queryset.filter(
            Q(staff__user__phone_number__icontains=value)
            | Q(staff__staff_number__icontains=value)
        )
class StaffLeaveApplicationFilter(django_filters.FilterSet):
    """
    Filter leave applications
    """

    search = django_filters.CharFilter(method="filter_by_all", label="Search")
    status = django_filters.CharFilter(field_name="status", lookup_expr="icontains")
    department = django_filters.NumberFilter(field_name="staff__department_id")

    class Meta:
        model = StaffLeaveApplication
        fields = ["status", "department", "search"]

    def filter_by_all(self, queryset, name, value):
        value = value.strip()
        return queryset.filter(
            Q(staff__user__phone_number__icontains=value)
            | Q(staff__staff_number__icontains=value)
        )
class StaffLeaveFilter(django_filters.FilterSet):
    """
    Filter leave 
    """

    search = django_filters.CharFilter(method="filter_by_all", label="Search")
    status = django_filters.CharFilter(field_name="status", lookup_expr="icontains")
    department = django_filters.NumberFilter(field_name="application__staff__department_id")

    class Meta:
        model = StaffLeave
        fields = ["status", "department", "search"]

    def filter_by_all(self, queryset, name, value):
        value = value.strip()
        return queryset.filter(
            Q(application__staff__user__phone_number__icontains=value)
            | Q(application__staff__staff_number__icontains=value)
        )


class PayslipFilter(django_filters.FilterSet):

   
    period_start = django_filters.DateFilter(
        method="filter_by_period", label="Filter Period Start"
    )
    period_end = django_filters.DateFilter(
        method="filter_by_period", label="Filter Period End"
    )
    status = django_filters.CharFilter(
        field_name="staff__status", lookup_expr="icontains"
    )
    department = django_filters.NumberFilter(field_name="staff__department_id")

    search = django_filters.CharFilter(method="filter_by_all", label="Search")

    class Meta:
        model = Payslip
        fields = ["period_start", "period_end", "status", "department", "search"]

    def filter_by_all(self, queryset, name, value):
        value = value.strip()
        return queryset.filter(
            Q(staff__staff_number__icontains=value)
            | Q(staff__user__phone_number__icontains=value)
        )

    def filter_by_period(self, queryset, name, value):
        period_start = self.data.get("period_start")
        period_end = self.data.get("period_end")
        if not period_start or not period_end:
            return queryset

        return queryset.filter(
            Q(payroll_period_start__lte=period_end),
            Q(payroll_period_end__gte=period_start),
        )
