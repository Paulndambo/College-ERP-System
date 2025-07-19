from rest_framework import serializers
from apps.schools.serializers import (
    ProgrammeCohortListSerializer,
    SemesterListSerializer,
)
from apps.students.models import SemesterReporting
from rest_framework.exceptions import ValidationError


class SemesterReportingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SemesterReporting
        fields = "__all__"


class CreateSemesterReportingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SemesterReporting
        fields = [
            "student",
            "semester",
        ]

    def validate(self, data):
        student = data["student"]
        semester = data["semester"]

        cohort = student.cohort
        if not cohort:
            raise ValidationError(
                {"error": "This student is not assigned to any cohort."}
            )

        if SemesterReporting.objects.filter(
            student=student, semester=semester, cohort=cohort
        ).exists():
            raise ValidationError(
                {"error": "This student has already  reported for the given semester."}
            )

        return data

    def create(self, validated_data):
        student = validated_data["student"]
        semester = validated_data["semester"]
        cohort = student.cohort

        reporting = SemesterReporting.objects.create(
            student=student,
            semester=semester,
            cohort=cohort,
            academic_year=cohort.get_academic_year(),
            reported=True,
        )
        return reporting


class SemesterReportingListSerializer(serializers.ModelSerializer):
    cohort = ProgrammeCohortListSerializer()
    semester = SemesterListSerializer()
    student = serializers.SerializerMethodField()
    reg_no = serializers.SerializerMethodField()

    class Meta:
        model = SemesterReporting
        fields = [
            "id",
            "cohort",
            "student",
            "reg_no",
            "academic_year",
            "semester",
            "reported",
            "created_on",
            "updated_on",
        ]

    def get_student(self, obj):
        return obj.student.name()

    def get_reg_no(self, obj):
        return obj.student.registration_number
