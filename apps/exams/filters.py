
from apps.exams.models import ExamData
import django_filters

class ExamDataFilterSet(django_filters.FilterSet):
    student = django_filters.NumberFilter(field_name='student_id')
    reg_no = django_filters.CharFilter(field_name='student__registration_number', lookup_expr='icontains')
    course_name = django_filters.CharFilter(field_name='course__name', lookup_expr='icontains')
    semester_name = django_filters.CharFilter(field_name='semester__name', lookup_expr='icontains')
    course = django_filters.NumberFilter(field_name='course_id')
    semester = django_filters.NumberFilter(field_name='semester_id')
    cohort = django_filters.NumberFilter(field_name='cohort_id')
    class Meta:
        model = ExamData
        fields = [
            'student', 
            'semester', 
            'cohort', 
            'course', 
            'reg_no'
         
        ]

class TranscriptsFilter(django_filters.FilterSet):
   
    programme = django_filters.NumberFilter(field_name='student__programme_id')
    semester = django_filters.NumberFilter(field_name='semester_id')
    cohort = django_filters.NumberFilter(field_name='cohort_id')
    reg_no = django_filters.CharFilter(field_name='student__registration_number')
    
    class Meta:
        model = ExamData
        fields = ['programme', 'semester', 'cohort', 'reg_no']