
import django_filters
from django.db.models import Q
from decimal import Decimal

from apps.finance.models import FeeStructure


class FeeStructureFilter(django_filters.FilterSet):
  
    semester = django_filters.NumberFilter(field_name="semester_id")
   
    class Meta:
        model = FeeStructure
        fields = ["semester", ]

   