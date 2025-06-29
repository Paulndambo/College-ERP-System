from apps.schools.models import Course, ProgrammeCohort, Semester
from apps.schools.serializers import (
    CourseListSerializer,
    ProgrammeCohortListSerializer,
    SemesterListSerializer,
)
from apps.students.models import Student
from apps.students.serializers import StudentListSerializer
from apps.users.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import ExamData


class ExamDataCreateSerializer(serializers.ModelSerializer):
    cohort = serializers.PrimaryKeyRelatedField(
        queryset=ProgrammeCohort.objects.all(), required=False
    )
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    semester = serializers.PrimaryKeyRelatedField(queryset=Semester.objects.all())

    class Meta:
        model = ExamData
        fields = [
            "student",
            "semester",
            "cohort",
            "course",
            "cat_one",
            "cat_two",
            "exam_marks",
            "recorded_by",
            "total_marks",
        ]
        extra_kwargs = {
            "recorded_by": {
                "required": False,
                "write_only": True,
            },
            "total_marks": {
                "required": False,
                "write_only": True,
            },
            "cohort": {
                "required": False,
                "write_only": True,
            },
        }

    def validate(self, data):
        student = data.get("student")
        semester = data.get("semester")
        course = data.get("course")

        if ExamData.objects.filter(
            student=student, semester=semester, course=course
        ).exists():
            raise ValidationError(
                "Marks for this student in the specified Unit and semester already exist."
            )

        cat_marks = (data.get("cat_one", 0) + data.get("cat_two", 0)) / 2
        data["total_marks"] = cat_marks + data.get("exam_marks", 0)
        return data


class ExamDataListSerializer(serializers.ModelSerializer):
    cohort = ProgrammeCohortListSerializer()
    course = CourseListSerializer()
    student = StudentListSerializer()
    semester = SemesterListSerializer()
    recorded_by = UserSerializer()

    class Meta:
        model = ExamData
        fields = [
            "id",
            "student",
            "semester",
            "cohort",
            "course",
            "cat_one",
            "cat_two",
            "recorded_by",
            "exam_marks",
            "total_marks",
            "grade",
        ]


class StudentExamDataSerializer(serializers.ModelSerializer):
    student = StudentListSerializer()

    class Meta:
        model = ExamData
        fields = ["student"]


class MinimalSemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ["id", "name", "academic_year", "status"]


class MinimalCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "course_code",
        ]


class MarkSerializer(serializers.ModelSerializer):
    course = MinimalCourseSerializer()
    grade = serializers.SerializerMethodField()

    class Meta:
        model = ExamData
        fields = [
            "id",
            "course",
            "cat_one",
            "cat_two",
            "exam_marks",
            "total_marks",
            "grade",
        ]

    def get_grade(self, obj):
        return obj.grade()
