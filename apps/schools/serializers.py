from rest_framework import serializers
from .models import School, Department, Programme, Course, Semester, ProgrammeCohort, CourseSession



class SchoolCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['name', 'email', 'phone', 'location']


class SchoolListSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'email', 'phone', 'location']


class DepartmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name', 'school', 'office']


class DepartmentListSerializer(serializers.ModelSerializer):
    school = SchoolListSerializer()
    class Meta:
        model = Department
        fields = ['id', 'name', 'school', 'office']
        
    def get_school(self, obj):
        return obj.school.name


class ProgrammeCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Programme
        fields = ['name', 'code', 'school', 'department', 'level']


class ProgrammeListSerializer(serializers.ModelSerializer):
    school = SchoolListSerializer()
    department = DepartmentListSerializer()
    class Meta:
        model = Programme
        fields = ['id', 'name', 'code', 'school', 'department', 'level']
        
    # def get_school(self, obj):
    #     return obj.school.name
    # def get_department(self, obj):
    #     return obj.department.name


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_code', 'name', 'school', 'department', 'programme']


class CourseListSerializer(serializers.ModelSerializer):
    school=SchoolListSerializer()
    department=DepartmentListSerializer()
    programme=ProgrammeListSerializer()
    class Meta:
        model = Course
        fields = ['id', 'course_code', 'name', 'school', 'department', 'programme']



class SemesterCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['name', 'academic_year', 'start_date', 'end_date', 'status']


class SemesterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ['id', 'name', 'academic_year', 'start_date', 'end_date', 'status']



class ProgrammeCohortCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgrammeCohort
        fields = ['name', 'programme', 'current_year', 'current_semester', 'status']


class ProgrammeCohortListSerializer(serializers.ModelSerializer):
    programme = ProgrammeListSerializer()
    current_semester = SemesterListSerializer()
    class Meta:
        model = ProgrammeCohort
        fields = ['id', 'name', 'programme', 'current_year', 'current_semester', 'status']
    
    def get_programme(self, obj):
        return obj.programme.name



class CourseSessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSession
        fields = ['cohort', 'course', 'start_time', 'period', 'status']


class CourseSessionListSerializer(serializers.ModelSerializer):
    cohort = serializers.StringRelatedField(source='cohort.name')
    course = serializers.StringRelatedField(source='course.name')
    class Meta:
        model = CourseSession
        fields = ['id', 'cohort', 'course', 'start_time', 'period', 'status']
