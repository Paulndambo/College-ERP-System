from rest_framework import serializers
from apps.core.models import StudyYear
from apps.core.serializers import StudyYearListSerializer
from apps.schools.models import ProgrammeCohort, Semester

from apps.schools.serializers import SemesterListSerializer
from apps.students.models import Promotion, SemesterReporting, StudentCourseEnrollment
from rest_framework.exceptions import ValidationError

from apps.students.serializers import StudentListSerializer
from apps.users.serializers import UserSerializer


class StudentCourseEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCourseEnrollment
        fields = "__all__"

class SemesterReportingListSerializer(serializers.ModelSerializer):
    student = StudentListSerializer()
    semester = SemesterListSerializer()
    done_by = UserSerializer()
    

    class Meta:
        model = SemesterReporting
        fields = ("id",
                  "student",
                  "semester",
                  "done_by",
                  "created_on",
                  "updated_on")
class PromotionListSerializer(serializers.ModelSerializer):
    student = StudentListSerializer()
    study_year = StudyYearListSerializer()
    done_by = UserSerializer()
    class Meta:
        model = Promotion
        fields = ("id",
                  "student",
                  "study_year",
                  "promoted_on",
                  "done_by",
                  "created_on",
                  "updated_on")


class ReportSemesterStudentsSerializer(serializers.Serializer):
    cohort = serializers.PrimaryKeyRelatedField(
        queryset=ProgrammeCohort.objects.all(), required=True  
    )
    semester = serializers.PrimaryKeyRelatedField(
        queryset=Semester.objects.all(), required=True
    )


class ReportSingleSemesterStudentSerializer(serializers.Serializer):
    registration_number = serializers.CharField(required=True)
    semester = serializers.PrimaryKeyRelatedField(
        queryset=Semester.objects.all(), required=True
    )


class PromoteStudentsSerializer(serializers.Serializer):
    cohort = serializers.PrimaryKeyRelatedField(
        queryset=ProgrammeCohort.objects.all(), required=True
    )
    study_year = serializers.PrimaryKeyRelatedField(
        queryset=StudyYear.objects.all(), required=True
    )

class GraduateStudentsSerializer(serializers.Serializer):
    cohort = serializers.PrimaryKeyRelatedField(
        queryset=ProgrammeCohort.objects.all(), required=True
    )
    
class GraduateSingleStudentSerializer(serializers.Serializer):
    registration_number = serializers.CharField(required=True)
    
class PromoteSingleStudentSerializer(serializers.Serializer):
    registration_number = serializers.CharField(required=True)
    study_year = serializers.PrimaryKeyRelatedField(
        queryset=StudyYear.objects.all(), required=True
    )