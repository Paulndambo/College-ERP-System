from .models import (
    Course,
    ProgrammeCohort,
    Department,
    Programme,
    School,
    CourseSession,
    Semester,
)
import django_filters


class CohortsFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="exact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="icontains")

    class Meta:
        model = ProgrammeCohort
        fields = [
            "name",
            "status",
        ]


class DepartmentFilter(django_filters.FilterSet):
    department_name = django_filters.CharFilter(field_name="name", lookup_expr="exact")
    school = django_filters.NumberFilter(field_name="school")

    class Meta:
        model = Department
        fields = ["department_name", "school"]


class SchoolFilter(django_filters.FilterSet):
    school_name = django_filters.CharFilter(field_name="name", lookup_expr="exact")

    class Meta:
        model = School
        fields = [
            "school_name",
        ]


class ProgrammeFilter(django_filters.FilterSet):
    programme_name = django_filters.CharFilter(field_name="name", lookup_expr="exact")
    department = django_filters.NumberFilter(field_name="department")

    class Meta:
        model = Programme
        fields = ["programme_name", "department"]


class CourseFilter(django_filters.FilterSet):
    course_name = django_filters.CharFilter(field_name="name", lookup_expr="exact")
    department = django_filters.NumberFilter(field_name="department")

    class Meta:
        model = Course
        fields = ["course_name", "department"]


class SemesterFilter(django_filters.FilterSet):
    semester_name = django_filters.CharFilter(field_name="name", lookup_expr="exact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")

    class Meta:
        model = Semester
        fields = ["semester_name", "status"]


class CourseSessionFilter(django_filters.FilterSet):
    course_name = django_filters.CharFilter(
        field_name="course__name", lookup_expr="exact"
    )
    status = django_filters.CharFilter(field_name="status", lookup_expr="exact")
    cohort = django_filters.NumberFilter(field_name="cohort")

    class Meta:
        model = CourseSession
        fields = ["course_name", "cohort", "status"]
