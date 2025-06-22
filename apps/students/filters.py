from .models import Student
import django_filters

from apps.schools.models import Course, Programme, Semester, Department
from django.db.models import Count, Q


class StudentFilter(django_filters.FilterSet):
    reg_no = django_filters.CharFilter(
        field_name="registration_number", lookup_expr="icontains"
    )
    programme = django_filters.NumberFilter(field_name="programme_id")
    department = django_filters.NumberFilter(field_name="programme__department_id")
    cohort = django_filters.NumberFilter(field_name="cohort_id")
    status = django_filters.CharFilter(field_name="status")
    semester = django_filters.NumberFilter(field_name="cohort__current_semester_id")

    class Meta:
        model = Student
        fields = ["reg_no", "programme", "cohort", "semester", "status"]


class AssessmentFilter(django_filters.FilterSet):
    reg_no = django_filters.CharFilter(
        field_name="registration_number", lookup_expr="icontains"
    )
    programme = django_filters.ModelChoiceFilter(
        queryset=Programme.objects.all().order_by("name"), field_name="programme"
    )
    department = django_filters.NumberFilter(field_name="programme__department_id")
    cohort = django_filters.NumberFilter(field_name="cohort_id")
    status = django_filters.CharFilter(field_name="status")

    semester = django_filters.ModelChoiceFilter(
        queryset=Semester.objects.all().order_by("name"), method="filter_by_semester"
    )

    # Direct course filter that works independently of programme
    course = django_filters.ModelChoiceFilter(
        queryset=Course.objects.all().order_by("name"), method="filter_by_course"
    )

    class Meta:
        model = Student
        fields = [
            "reg_no",
            "programme",
            "department",
            "cohort",
            "status",
            "semester",
            "course",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Always keep all courses available regardless of programme selection
        self.filters["course"].queryset = Course.objects.all().order_by("name")

        # If programme is selected, update the display but don't make it dependent
        if "programme" in self.data and self.data["programme"]:
            try:
                programme_id = int(self.data["programme"])
                # We no longer limit the course queryset here
            except (ValueError, TypeError):
                pass

    def filter_by_semester(self, queryset, name, value):
        """
        Filter students by semester
        """
        if value:
            return queryset.filter(cohort__current_semester=value)
        return queryset

    def filter_by_course(self, queryset, name, value):
        """
        Filter students directly by course
        This will find all students enrolled in programmes that have this course,
        completely independent of programme selection
        """
        if not value:
            return queryset

        # Find the programme(s) that offer this course
        # This allows for cases where a course might be offered in multiple programmes
        programmes_with_course = Programme.objects.filter(
            course__id=value.id
        ).values_list("id", flat=True)

        # Get all students in those programmes
        return queryset.filter(programme_id__in=programmes_with_course).distinct()
