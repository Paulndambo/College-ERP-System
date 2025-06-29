from apps.core.serializers import CampusListSerializer
from apps.marketing.serializers import LeadListDetailSerializer
from apps.schools.serializers import ProgrammeListSerializer
from rest_framework import serializers
from .models import (
    Intake,
    StudentApplication,
    ApplicationDocument,
    ApplicationEducationHistory,
)
from rest_framework.exceptions import ValidationError


class IntakeCreateSerializer(serializers.ModelSerializer):
    closed = serializers.BooleanField(default=False)
    class Meta:
        model = Intake
        fields = ["name", "start_date", "end_date", "closed"]


class IntakeListDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intake
        fields = "__all__"


class ApplicationDocumentCreateSerializer(serializers.ModelSerializer):
    student_application = serializers.PrimaryKeyRelatedField(
        queryset=StudentApplication.objects.all(), required=False
    )

    class Meta:
        model = ApplicationDocument
        fields = [
            "student_application",
            "document_name",
            "document_type",
            "document_file",
            "verified",
        ]
        extra_kwargs = {
            "verified": {"required": False},
        }


class ApplicationDocumentListDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDocument
        fields = "__all__"


class ApplicationEducationHistoryCreateSerializer(serializers.ModelSerializer):
    student_application = serializers.PrimaryKeyRelatedField(
        queryset=StudentApplication.objects.all(), required=False
    )
    graduated = serializers.BooleanField(default=False)

    class Meta:
        model = ApplicationEducationHistory
        fields = [
            "student_application",
            "institution",
            "level",
            "grade_or_gpa",
            "year",
            "major",
            "graduated",
        ]
        extra_kwargs = {
            "major": {"required": False},
            "student_application": {"required": False},
        }


class ApplicationEducationHistoryListDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationEducationHistory
        fields = "__all__"


class StudentApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentApplication
        fields = [
            "application_number",
            "lead",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "id_number",
            "passport_number",
            "date_of_birth",
            "gender",
            "first_choice_programme",
            "second_choice_programme",
            "guardian_name",
            "guardian_email",
            "guardian_relationship",
            "guardian_phone_number",
            "address",
            "postal_code",
            "city",
            "country",
            "passport_photo",
            "intake",
            "status",
            "campus",
        ]
        read_only_fields = ["slug"]
        extra_kwargs = {
            "intake": {"required": False},
            "passport_photo": {"required": False},
            "campus": {"required": False},
            "first_choice_programme": {"required": False},
            "application_number": {
                "required": False,
            },
            "second_choice_programme": {"required": False},
        }

    def validate(self, attrs):
        intake = attrs.get("intake")
        if intake and intake.closed:
            raise ValidationError("This intake is already closed for applications.")
        return attrs

    def create(self, validated_data):
        return StudentApplication.objects.create(**validated_data)


class StudentApplicationListDetailSerializer(serializers.ModelSerializer):
    first_choice_programme = ProgrammeListSerializer(read_only=True)
    second_choice_programme = ProgrammeListSerializer(read_only=True)
    campus = CampusListSerializer(read_only=True)
    lead = LeadListDetailSerializer(read_only=True)
    intake = IntakeListDetailSerializer(read_only=True)

    application_education_history = serializers.SerializerMethodField()
    application_document = serializers.SerializerMethodField()

    class Meta:
        model = StudentApplication
        fields = [
            "id",
            "application_number",
            "lead",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "id_number",
            "passport_number",
            "date_of_birth",
            "gender",
            "first_choice_programme",
            "second_choice_programme",
            "guardian_name",
            "guardian_email",
            "guardian_relationship",
            "guardian_phone_number",
            "address",
            "postal_code",
            "city",
            "country",
            "passport_photo",
            "intake",
            "status",
            "slug",
            "campus",
            "created_on",
            "updated_on",
            "application_education_history",
            "application_document",
        ]

    def get_application_education_history(self, obj):

        education_history = ApplicationEducationHistory.objects.filter(
            student_application=obj
        )
        return ApplicationEducationHistoryListDetailSerializer(
            education_history, many=True
        ).data

    def get_application_document(self, obj):

        documents = ApplicationDocument.objects.filter(student_application=obj)
        return ApplicationDocumentListDetailSerializer(documents, many=True).data


class StudentEnrollmentSerializer(serializers.Serializer):

    application_id = serializers.IntegerField(required=True)
    cohort_id = serializers.IntegerField(required=True)
    campus_id = serializers.IntegerField(required=True)

    def validate(self, data):

        application_id = data.get("application_id")

        try:
            application = StudentApplication.objects.get(id=application_id)

            if application.status == "Enrolled":
                raise serializers.ValidationError(
                    "This application has already been enrolled"
                )

            if application.status != "Accepted":
                raise serializers.ValidationError(
                    "Only Accepted applications can be enrolled"
                )

        except StudentApplication.DoesNotExist:
            raise serializers.ValidationError("Student application not found")

        return data
