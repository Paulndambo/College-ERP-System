from rest_framework import serializers

from apps.students.models import (
    MealCard, StudentAttendance, SemesterReporting
)
from apps.exams.models import ExamData


############# Student Related Serializers ############
class MealCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealCard
        fields = '__all__'


class StudentAttendanceSerializer(serializers.ModelSerializer):
    course = serializers.SerializerMethodField()
    course_code = serializers.SerializerMethodField()
    semester = serializers.SerializerMethodField()
    academic_year = serializers.SerializerMethodField()
    class Meta:
        model = StudentAttendance
        fields = '__all__'

    
    def get_course(self, obj):
        return obj.session.course.name if obj.session and obj.session.course else None
    
    def get_course_code(self, obj):
        return obj.session.course.course_code if obj.session and obj.session.course else None
    
    def get_semester(self, obj):
        return obj.session.semester.name if obj.session and obj.session.semester else None
    
    def get_academic_year(self, obj):
        return obj.session.cohort.get_academic_year() if obj.session and obj.session.cohort else None


class SemesterReportingSerializer(serializers.ModelSerializer):
    semester = serializers.StringRelatedField()
    class Meta:
        model = SemesterReporting
        fields = '__all__'


class ExamDataSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.name', read_only=True)
    semester_name = serializers.CharField(source='semester.name', read_only=True)
    cohort_name = serializers.CharField(source='cohort.name', read_only=True)
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    academic_year = serializers.CharField(source='semester.academic_year', read_only=True)
    grade = serializers.CharField(read_only=True)

    class Meta:
        model = ExamData
        fields = "__all__"

   