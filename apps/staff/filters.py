from .models import Staff
import django_filters

from apps.schools.models import Course, Programme, Semester, Department
from django.db.models import Count, Q


class StaffFilter(django_filters.FilterSet):
    staff_no = django_filters.CharFilter(field_name='staff_number', lookup_expr='icontains')    
    class Meta:
        model = Staff
        fields = ['staff_no']

