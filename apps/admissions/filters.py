import django_filters
from .models import (
    Intake,
    StudentApplication,
    ApplicationDocument,
    ApplicationEducationHistory,
)


class IntakeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Intake
        fields = ["name"]


class StudentApplicationFilter(django_filters.FilterSet):
    application_no = django_filters.CharFilter(
        field_name="application_number", lookup_expr="icontains"
    )
    phone_no = django_filters.CharFilter(
        field_name="phone_number", lookup_expr="icontains"
    )
    status = django_filters.CharFilter(field_name="status")
    intake = django_filters.NumberFilter(field_name="intake_id")
    campus = django_filters.NumberFilter(field_name="campus_id")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"Filter initialized with data: {args[0] if args else 'No args'}")

    def filter_queryset(self, queryset):
        print(f"Before filtering: {queryset.count()} records")
        filtered = super().filter_queryset(queryset)
        print(f"After filtering: {filtered.count()} records")
        return filtered

    class Meta:
        model = StudentApplication
        fields = [
            "application_no",
            "phone_no",
            "status",
            "intake",
            "campus",
        ]


class ApplicationDocumentFilter(django_filters.FilterSet):
    student_application = django_filters.NumberFilter()
    document_type = django_filters.ChoiceFilter(
        choices=[
            ("Transcript", "Transcript"),
            ("Certificate", "Certificate"),
            ("Identification", "Identification"),
        ]
    )
    document_name = django_filters.CharFilter(lookup_expr="icontains")
    verified = django_filters.BooleanFilter()

    class Meta:
        model = ApplicationDocument
        fields = ["student_application", "document_type", "document_name", "verified"]


class ApplicationEducationHistoryFilter(django_filters.FilterSet):
    student_application = django_filters.NumberFilter()
    institution = django_filters.CharFilter(lookup_expr="icontains")
    level = django_filters.ChoiceFilter(
        choices=[
            ("Primary School", "Primary School"),
            ("Secondary School", "Secondary School"),
            ("Undergraduate", "Undergraduate"),
            ("Graduate", "Graduate"),
        ]
    )
    graduated = django_filters.BooleanFilter()

    class Meta:
        model = ApplicationEducationHistory
        fields = ["student_application", "institution", "level", "graduated"]
