from apps.schools.models import Course
from apps.students.models import StudentCourseEnrollment

from rest_framework import serializers

class CourseSerializer(serializers.ModelSerializer):
    semester_name = serializers.SerializerMethodField()
    class Meta:
        model = Course
        fields = '__all__'

    def get_semester_name(self, obj):
        return obj.semester if obj.semester else None


class StudentCourseEnrollmentSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_type = serializers.CharField(source='course.course_type', read_only=True)
    semester_name = serializers.SerializerMethodField()
    academic_year = serializers.SerializerMethodField()
    class Meta:
        model = StudentCourseEnrollment
        fields = "__all__"

    def get_semester_name(self, obj):
        return obj.semester.name if obj.semester else None
    
    def get_academic_year(self, obj):
        return obj.semester.academic_year if obj.semester else None