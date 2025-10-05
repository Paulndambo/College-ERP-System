from apps.schools.models import Programme, ProgrammeCohort

from apps.schools.serializers import DepartmentListSerializer
from apps.users.models import User
from apps.users.serializers import UserSerializer
from rest_framework import serializers
from .models import *


class StaffCreateSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), required=True
    )
    position = serializers.PrimaryKeyRelatedField(
        queryset=StaffPosition.objects.all(), required=False
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False
    )

    class Meta:
        model = Staff
        fields = [
            "user",
            # "staff_number",
            "department",
            "position",
        ]
        extra_kwargs = {
            "user": {"required": False},
            "position": {"required": False},
        }


class StaffStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ["id", "status"]

    def validate_status(self, value):
        allowed_statuses = ["Active", "Inactive"]
        if value not in allowed_statuses:
            raise serializers.ValidationError(
                "Status must be either 'Active' or 'Inactive'"
            )
        return value


class StaffDocumentCreateSerializer(serializers.ModelSerializer):
    staff = serializers.PrimaryKeyRelatedField(
        queryset=Staff.objects.all(),
    )

    class Meta:
        model = StaffDocuments
        fields = ["staff", "document_type", "document_file", "notes"]




class SingleStaffDocumentSerializer(serializers.Serializer):
    document_type = serializers.CharField()
    document_file = serializers.FileField()
    notes = serializers.CharField(required=False, allow_blank=True)




class StaffDocumentListSerializer(StaffDocumentCreateSerializer):
    class Meta:
        model = StaffDocuments
        fields = [
            "id",
            "staff",
            "document_type",
            "document_file",
            "notes",
            "created_on",
            "updated_on",
        ]


class StaffPositionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffPosition
        fields = ["id", "name", "created_on", "updated_on"]


class CreateStaffPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffPosition
        fields = ["name"]



class StaffListDetailSerializer(serializers.ModelSerializer):
    department = DepartmentListSerializer()
    user = UserSerializer()
    position = StaffPositionListSerializer()
 

    class Meta:
        model = Staff
        fields = [
            "id",
            "user",
            "staff_number",
            "department",
            "position",
            "status",
         
            "created_on",
            "updated_on",
        ]
        extra_kwargs = {
            "user": {"required": False},
        }



class StaffPaySlipSerializer(serializers.ModelSerializer):
    staff = StaffListDetailSerializer()
    outstanding_balance = serializers.SerializerMethodField()
    payment_status_label = serializers.SerializerMethodField()
    class Meta:
        model = Payslip
        fields = [
            "id",
            "staff",
            "basic_salary",
            "total_deductions",
            "total_overtime",
            "payroll_period_start",
            "payroll_period_end",
            "total_allowances",
            "net_pay",
            "nssf",
            "nhif",
            "paye",
            "generated_at",
            "created_on",
            "updated_on",
            "payment_status",
            "outstanding_balance",
            "payment_status_label",
        ]
    def get_outstanding_balance(self, obj):
        if hasattr(obj, "payment_statement"):
            return obj.payment_statement.outstanding_balance
        return None
    def get_payment_status_label(self, obj):
        return obj.get_payment_status_display()

class CreateStaffLeaveApplicationSerializer(serializers.ModelSerializer):
    staff = serializers.PrimaryKeyRelatedField(
        queryset=Staff.objects.all(),
        required=False,
    )

    class Meta:
        model = StaffLeaveApplication
        fields = [
            "id",
            "reason_declined",
            "start_date",
            "end_date",
            "staff",
            "reason",
            "leave_type",
            "status",
        ]
        extra_kwargs = {
            "reason_declined": {"required": False},
            "status": {"required": False},
        }

    def validate(self, attrs):
        request = self.context.get("request")
        is_update = request and request.method in ["PUT", "PATCH"]

        staff = attrs.get("staff")
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if not is_update:
            if not start_date or not end_date:
                raise serializers.ValidationError("Start and end dates are required.")

            leave_days = (end_date - start_date).days + 1

            if staff:
                entitlement = StaffLeaveEntitlement.objects.filter(
                    staff=staff, year=start_date.year
                ).first()

                if not entitlement:
                    raise serializers.ValidationError(
                        "No leave entitlement record found."
                    )

                if (
                    attrs.get("leave_type") != "Emergency"
                    and leave_days > entitlement.remaining_days
                ):
                    raise serializers.ValidationError(
                        f"Leave exceeds remaining days. You have {entitlement.remaining_days} days remaining."
                    )

        return attrs


class StaffLeaveApplicationListSerializer(serializers.ModelSerializer):
    staff = StaffListDetailSerializer()
    leave_days_applied_for = serializers.SerializerMethodField()

    class Meta:
        model = StaffLeaveApplication
        fields = [
            "id",
            "reason_declined",
            "start_date",
            "end_date",
            "staff",
            "reason",
            "leave_type",
            "status",
            "leave_days_applied_for",
        ]
        extra_kwargs = {
            "reason_declined": {"required": False},
        }

    def get_leave_days_applied_for(self, obj):
        return obj.leave_days_applied_for()


class StaffLeaveSerializer(serializers.ModelSerializer):
    application = StaffLeaveApplicationListSerializer()

    class Meta:
        model = StaffLeave
        fields = [
            "id",
            "application",
            "created_on",
            "reason_cancelled",
            "status",
            "updated_on",
        ]


class CreateUpdateStaffLeaveSerializer(serializers.ModelSerializer):
    application = serializers.PrimaryKeyRelatedField(
        queryset=StaffLeaveApplication.objects.all(), required=False
    )

    class Meta:
        model = StaffLeave
        fields = [
            "reason_cancelled",
            "application",
            "status",
        ]


class StaffLeaveEntitlementCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating staff leave entitlements"""

    staff = serializers.PrimaryKeyRelatedField(queryset=Staff.objects.all())

    class Meta:
        model = StaffLeaveEntitlement
        fields = ["staff", "year", "total_days", "used_days"]
        extra_kwargs = {
            "total_days": {"required": True},
            "used_days": {"required": False},
            "staff": {"required": False},
        }

    def validate_staff(self, value):
        """Ensure staff exists and is active"""
        if not Staff.objects.filter(id=value.id, status="Active").exists():
            raise serializers.ValidationError("Staff member must be active")
        return value

    def validate_used_days(self, value):
        """Ensure used days is not negative"""
        if value < 0:
            raise serializers.ValidationError("Used days cannot be negative")
        return value

    def validate_total_days(self, value):
        """Ensure total days is positive"""
        if value <= 0:
            raise serializers.ValidationError("Total days must be greater than 0")
        return value

    def validate(self, attrs):
        """Ensure used days doesn't exceed total days"""
        used_days = attrs.get("used_days", 0)
        total_days = attrs.get("total_days")

        if used_days > total_days:
            raise serializers.ValidationError("Used days cannot exceed total days")
        return attrs


class StaffLeaveEntitlementDetailSerializer(serializers.ModelSerializer):
    """Serializer for listing staff leave entitlement details"""

    staff = StaffListDetailSerializer()
    remaining_days = serializers.ReadOnlyField()

    class Meta:
        model = StaffLeaveEntitlement
        fields = [
            "id",
            "staff",
            "year",
            "total_days",
            "used_days",
            "remaining_days",
        ]


class OvertimeRecordsListSerializer(serializers.ModelSerializer):
    staff = StaffListDetailSerializer()

    class Meta:
        model = OvertimeRecords
        fields = [
            "id",
            "date",
            "hours",
            "rate_per_hour",
            "approved",
            "staff",
        ]


class CreateOvertimeRecordSerializer(serializers.ModelSerializer):
    staff = serializers.PrimaryKeyRelatedField(queryset=Staff.objects.all())

    class Meta:
        model = OvertimeRecords
        fields = [
            "date",
            "hours",
            "rate_per_hour",
            "approved",
            "staff",
        ]
        extra_kwargs = {
            "approved": {"required": False},
        }


class ApproveOvertimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OvertimeRecords
        fields = ["approved"]
