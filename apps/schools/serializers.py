from rest_framework import serializers

from apps.core.models import AcademicYear, StudyYear
from apps.core.serializers import AcademicYearListSerializer, StudyYearListSerializer


from .models import (
    School,
    Department,
    Programme,
    Course,
    Semester,
    ProgrammeCohort,
    CourseSession,
)

class SemesterListSerializer(serializers.ModelSerializer):
    academic_year = AcademicYearListSerializer()

    class Meta:
        model = Semester
        fields = ["id", "name", "academic_year", "start_date", "end_date", "status"]

class SchoolCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ["name", "email", "phone", "location"]


class SchoolListSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ["id", "name", "email", "phone", "location"]


class DepartmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["name", "school", "office", "department_type"]


class DepartmentListSerializer(serializers.ModelSerializer):
    school = SchoolListSerializer()

    class Meta:
        model = Department
        fields = ["id", "name", "school", "office", "department_type"]

    def get_school(self, obj):
        return obj.school.name


class ProgrammeCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Programme
        fields = ["name", "code", "school", "department", "level"]


class ProgrammeListSerializer(serializers.ModelSerializer):
    school = SchoolListSerializer()
    department = DepartmentListSerializer()

    class Meta:
        model = Programme
        fields = ["id", "name", "code", "school", "department", "level"]


class CourseCreateSerializer(serializers.ModelSerializer):
    school = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.all(), required=True
    )
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), required=True
    )
    programme = serializers.PrimaryKeyRelatedField(
        queryset=Programme.objects.all(), required=True
    )
    study_year = serializers.PrimaryKeyRelatedField(
        queryset=StudyYear.objects.all(), required=True
    )
    semester = serializers.PrimaryKeyRelatedField(
        queryset=Semester.objects.all(), 
        required=False,
        allow_null=True
    )

    class Meta:
        model = Course
        fields = [
            "course_code",
            "name",
            "school",
            "department",
            "programme",
            "study_year",
            "semester",
            "course_type",
        ]
        extra_kwargs ={
               "semester": {
                "required": False
            },
        }


class MinimalClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "course_code", "name"]


class CourseListSerializer(serializers.ModelSerializer):
    school = SchoolListSerializer()
    department = DepartmentListSerializer()
    programme = ProgrammeListSerializer()
    study_year = StudyYearListSerializer()
    semester = SemesterListSerializer()
    class Meta:
        model = Course
        fields = ["id", 
                  "course_code",
                  "name",
                  "school",
                  "department",
                  "programme",
                  "study_year",
                  "semester",
                  ]


class ProgrammeListDetailSerializer(serializers.ModelSerializer):
    school = SchoolListSerializer()
    department = DepartmentListSerializer()
    units = CourseListSerializer(source="course_set", many=True, read_only=True)

    class Meta:
        model = Programme
        fields = ["id", "name", "code", "school", "department", "level", "units"]

    # def get_courses(self, obj):
    #     units = obj.course_set.filter(active=True)
    #     return CourseListSerializer(units, many=True)


class SemesterCreateSerializer(serializers.ModelSerializer):
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all()
    )

    class Meta:
        model = Semester
        fields = ["name", "start_date", "end_date", "academic_year", "status"]




class ProgrammeCohortCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgrammeCohort
        fields = [
            "name",
            "programme",
            "current_year",
            "current_semester",
            "intake",
            "status",
        ]


class ProgrammeCohortListSerializer(serializers.ModelSerializer):
    programme = ProgrammeListSerializer()
    current_semester = SemesterListSerializer()
    intake = serializers.SerializerMethodField()
    current_year = StudyYearListSerializer()
    class Meta:
        model = ProgrammeCohort
        fields = [
            "id",
            "name",
            "programme",
            "current_year",
            "current_semester",
            "status",
            "intake",
        ]

    def get_intake(self, obj):
        from apps.admissions.serializers import IntakeListDetailSerializer

        return IntakeListDetailSerializer(obj.intake).data

    def get_programme(self, obj):
        return obj.programme.name


class CourseSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSession
        fields = ["cohort", "course", "start_time", "period", "status"]


class CourseSessionListSerializer(serializers.ModelSerializer):
    cohort = ProgrammeCohortListSerializer()
    course = CourseListSerializer()

    class Meta:
        model = CourseSession
        fields = ["id", "cohort", "course", "start_time", "period", "status"]
