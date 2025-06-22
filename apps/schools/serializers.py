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
        
   


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_code', 'name', 'school', 'department', 'programme']

class MinimalClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'course_code', 'name']
class CourseListSerializer(serializers.ModelSerializer):
    school=SchoolListSerializer()
    department=DepartmentListSerializer()
    programme=ProgrammeListSerializer()
    class Meta:
        model = Course
        fields = ['id', 'course_code', 'name', 'school', 'department', 'programme']
    
class ProgrammeListDetailSerializer(serializers.ModelSerializer):
    school = SchoolListSerializer()
    department = DepartmentListSerializer()
    units = CourseListSerializer(source='course_set', many=True, read_only=True)
    
    class Meta:
        model = Programme
        fields = ['id', 'name', 'code', 'school', 'department', 'level', 'units']
        
    # def get_courses(self, obj):
    #     units = obj.course_set.filter(active=True)  
    #     return CourseListSerializer(units, many=True)


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
    cohort = ProgrammeCohortListSerializer()
    course = CourseListSerializer()
    class Meta:
        model = CourseSession
        fields = ['id', 'cohort', 'course', 'start_time', 'period', 'status']
