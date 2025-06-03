
from apps.schools.models import Programme, ProgrammeCohort

from apps.users.models import User
from apps.users.serializers import UserSerializer
from rest_framework import serializers
from .models import *


class StaffDepartmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"
class StaffCreateSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), required=False)
    class Meta:
        model = Staff
        fields = [
            'user',
            'staff_number', 
            'department',
            'position',
        ]
        extra_kwargs = {
            'user': {'required': False},
            'position': {'required': False},
        }


class StaffListDetailSerializer(serializers.ModelSerializer):
    department = StaffDepartmentListSerializer()
    # user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    user = UserSerializer()
    class Meta:
        model = Staff
        fields = [
            'id',
            'user',
            'staff_number', 
            'department',
            'position',
        ]
        extra_kwargs = {
            'user': {'required': False},
        }
        
class CreateStaffLeaveApplicationSerializer(serializers.ModelSerializer):
    staff = serializers.PrimaryKeyRelatedField(queryset=Staff.objects.all(), required=False)
    class Meta:
        model = StaffLeaveApplication
        fields = [
            'id',
            'reason_declined',
            'start_date',
            'end_date',
            'staff',
            'reason',
            'leave_type',
            'status',
        ]
        extra_kwargs = {
            'reason_declined': {'required': False},
            'status': {'required': False},
        }

class StaffLeaveApplicationListSerializer(serializers.ModelSerializer):
    staff = StaffListDetailSerializer()
    class Meta:
        model = StaffLeaveApplication
        fields = [
            'id',
            'reason_declined',
            'start_date',
            'end_date',
            'staff',
            'reason',
            'leave_type',
            'status',
        ]
        extra_kwargs = {
            'reason_declined': {'required': False},
        }
        
        
class StaffLeaveSerializer(serializers.ModelSerializer):
    application = StaffLeaveApplicationListSerializer()
    class Meta:
        model = StaffLeave
        fields = [
            'id',
            'application',
            'created_on',
            'reason_cancelled',
            'status',
            'updated_on',
        ]
        
class CreateUpdateStaffLeaveSerializer(serializers.ModelSerializer):
    application = serializers.PrimaryKeyRelatedField(queryset=StaffLeaveApplication.objects.all(), required=False)
    class Meta:
        model = StaffLeave
        fields = [
            'reason_cancelled',
            'application',
            'status',
        ]