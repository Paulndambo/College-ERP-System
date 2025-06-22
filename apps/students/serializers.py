from apps.users.serializers import UserSerializer
from rest_framework import serializers
from .models import *

class StudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'user',
            'registration_number', 
            'guardian_name',
            'guardian_phone_number', 
            'guardian_relationship', 
            'guardian_email',
            'status', 
            'programme', 
            'cohort', 
            'hostel_room', 
            'campus'
        ]
        extra_kwargs = {
            'user': {'required': False}
        }
class StudentListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, many=True)
    programme_name = serializers.CharField(source='programme.name', read_only=True)
    cohort_name = serializers.CharField(source='cohort.name', read_only=True)
    hostel_room_number = serializers.CharField(source='hostel_room.room_number', read_only=True)
    campus_name = serializers.CharField(source='campus.name', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 
            'user', 
            'registration_number', 
            'guardian_name',
            'guardian_phone_number', 
            'guardian_relationship', 
            'guardian_email',
            'status', 
            'programme_name', 
            'cohort_name',
            'hostel_room_number', 
            'campus_name'
        ]
        
class StudentEducationHistoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEducationHistory
        fields = '__all__'

class StudentEducationHistoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEducationHistory
        fields = '__all__'


class StudentDocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDocument
        fields = '__all__'

class StudentDocumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDocument
        fields = '__all__'


class MealCardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealCard
        fields = '__all__'

class MealCardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealCard
        fields = '__all__'


class StudentProgrammeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProgramme
        fields = '__all__'

class StudentProgrammeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProgramme
        fields = '__all__'


class StudentAttendanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAttendance
        fields = '__all__'

class StudentAttendanceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAttendance
        fields = '__all__'

class StudentCheckInCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCheckIn
        fields = '__all__'

class StudentCheckInListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCheckIn
        fields = '__all__'
