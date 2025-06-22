
import django_filters
from django.db.models import Q

from apps.students.models import SemesterReporting


class SemesterReportingFilter(django_filters.FilterSet):
    """
    Filter semester reporting records
    """
    
    search = django_filters.CharFilter(method="filter_by_all", label="Search")
    semester = django_filters.NumberFilter(field_name="semester_id")
    cohort = django_filters.NumberFilter(field_name="cohort_id")
    # academic_year = django_filters.CharFilter(field_name="academic_year", lookup_expr="icontains")
    # programme = django_filters.NumberFilter(field_name="student__programme_id")
    department = django_filters.NumberFilter(field_name="student__programme__department_id")
    

 
    class Meta:
        model = SemesterReporting
        fields = [
            "search",
            "semester",
            "cohort",
            "department",
        ]

    def filter_by_all(self, queryset, name, value):
        """
        Filter reporting records by student registration number, student name, or semester name
        """
        value = value.strip()
        return queryset.filter(
            Q(student__registration_number__icontains=value)
            | Q(student__user__first_name__icontains=value)
            | Q(student__user__last_name__icontains=value)
            
            
        )