from .models import Campus, StudyYear
import django_filters


class CampusFilter(django_filters.FilterSet):
    campus_name = django_filters.CharFilter(field_name="name", lookup_expr="exact")

    class Meta:
        model = Campus
        fields = [
            "campus_name",
        ]


class AcademicYearsFilter(django_filters.FilterSet):
    year_name = django_filters.CharFilter(field_name="name", lookup_expr="exact")

    class Meta:
        model = StudyYear
        fields = [
            "year_name",
        ]
