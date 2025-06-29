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

    def create(self, validated_data):

        document = super().create(validated_data)

        self._update_documents_uploaded_status(document.staff)

        return document

    def _update_documents_uploaded_status(self, staff):

        required_document_types = [
            "KRA_PIN",
            "ID",
            "NSSF",
            "NHIF",
            "Career Certifications",
        ]

        uploaded_document_types = (
            StaffDocuments.objects.filter(staff=staff)
            .values_list("document_type", flat=True)
            .distinct()
        )

        all_required_uploaded = all(
            doc_type in uploaded_document_types for doc_type in required_document_types
        )

        if all_required_uploaded:
            try:
                onboarding_progress = StaffOnboardingProgress.objects.get(staff=staff)
                if not onboarding_progress.documents_uploaded:
                    onboarding_progress.documents_uploaded = True
                    onboarding_progress.save()

            except StaffOnboardingProgress.DoesNotExist:

                StaffOnboardingProgress.objects.create(
                    staff=staff, documents_uploaded=True
                )


class SingleStaffDocumentSerializer(serializers.Serializer):
    document_type = serializers.CharField()
    document_file = serializers.FileField()
    notes = serializers.CharField(required=False, allow_blank=True)


class StaffDocumentMultiCreateSerializer(serializers.Serializer):
    staff = serializers.PrimaryKeyRelatedField(queryset=Staff.objects.all())
    documents = SingleStaffDocumentSerializer(many=True)

    def create(self, validated_data):
        staff = validated_data["staff"]
        documents_data = validated_data["documents"]
        print("documents_data", documents_data)

        created_documents = []
        for doc_data in documents_data:
            document = StaffDocuments.objects.create(
                staff=staff,
                document_type=doc_data["document_type"],
                document_file=doc_data["document_file"],
                notes=doc_data.get("notes", ""),
            )
            created_documents.append(document)

        self._update_documents_uploaded_status(staff)
        return created_documents

    def _update_documents_uploaded_status(self, staff):
        required_document_types = [
            "KRA_PIN",
            "ID",
            "NSSF",
            "NHIF",
            "Career Certifications",
        ]
        uploaded_document_types = (
            StaffDocuments.objects.filter(staff=staff)
            .values_list("document_type", flat=True)
            .distinct()
        )

        all_required_uploaded = all(
            doc_type in uploaded_document_types for doc_type in required_document_types
        )

        if all_required_uploaded:
            try:
                onboarding_progress = StaffOnboardingProgress.objects.get(staff=staff)
                if not onboarding_progress.documents_uploaded:
                    onboarding_progress.documents_uploaded = True
                    onboarding_progress.save()
            except StaffOnboardingProgress.DoesNotExist:
                StaffOnboardingProgress.objects.create(
                    staff=staff, documents_uploaded=True
                )


class CompleteOnboardingSerializer(serializers.ModelSerializer):
    """
    Serializer for marking onboarding as complete
    This is the final step that sets onboarding_completed = True
    """

    class Meta:
        model = StaffOnboardingProgress
        fields = ["id", "onboarding_completed"]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):

        if validated_data.get("onboarding_completed", False):
            if not (
                instance.user_created
                and instance.staff_details_completed
                and instance.payroll_setup_completed
                and instance.documents_uploaded
            ):
                raise serializers.ValidationError(
                    {
                        "onboarding_completed": "Cannot complete onboarding. All prerequisite steps must be completed first.",
                        "missing_steps": self._get_missing_steps(instance),
                    }
                )

            instance.onboarding_completed = True
            instance.save()

            staff = instance.staff
            if staff.onboarding_status != "Completed":
                staff.onboarding_status = "Completed"
                staff.status = "Active"
                staff.save()

        return instance

    def _get_missing_steps(self, instance):
        """Return list of incomplete onboarding steps"""
        missing_steps = []
        if not instance.user_created:
            missing_steps.append("user_created")
        if not instance.staff_details_completed:
            missing_steps.append("staff_details_completed")
        if not instance.payroll_setup_completed:
            missing_steps.append("payroll_setup_completed")
        if not instance.documents_uploaded:
            missing_steps.append("documents_uploaded")
        return missing_steps


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

class StaffOnboardingProgressSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffOnboardingProgress
        fields = [
            "id",
            "user_created",
            "staff_details_completed",
            "documents_uploaded",
            "payroll_setup_completed",
            "onboarding_completed",
            "created_on",
            "updated_on",
        ]


class StaffListDetailSerializer(serializers.ModelSerializer):
    department = DepartmentListSerializer()
    user = UserSerializer()
    position = StaffPositionListSerializer()
    onboarding_progress = serializers.SerializerMethodField()

    class Meta:
        model = Staff
        fields = [
            "id",
            "user",
            "staff_number",
            "department",
            "position",
            "status",
            "onboarding_status",
            "onboarding_progress",
            "created_on",
            "updated_on",
        ]
        extra_kwargs = {
            "user": {"required": False},
        }

    def get_onboarding_progress(self, obj):
        try:
            onboarding_progress = StaffOnboardingProgress.objects.get(staff=obj)
            return StaffOnboardingProgressSimpleSerializer(onboarding_progress).data
        except StaffOnboardingProgress.DoesNotExist:
            return None


class StaffOnboardingProgressListSerializer(serializers.ModelSerializer):
    staff = StaffListDetailSerializer()

    class Meta:
        model = StaffOnboardingProgress
        fields = [
            "id",
            "staff",
            "user_created",
            "staff_details_completed",
            "documents_uploaded",
            "payroll_setup_completed",
            "onboarding_completed",
            "created_on",
            "updated_on",
        ]
        extra_kwargs = {
            "staff": {"required": False},
        }


class StaffPayrollCreateSerializer(serializers.ModelSerializer):
    staff = serializers.PrimaryKeyRelatedField(queryset=Staff.objects.all())

    class Meta:
        model = StaffPayroll
        fields = [
            "id",
            "staff",
            "basic_salary",
            "house_allowance",
            "transport_allowance",
            "other_allowances",
            "nssf_number",
            "nhif_number",
            "kra_pin",
            "bank_name",
            "bank_account_number",
            "mpesa_number",
            "payment_frequency",
        ]

    def validate_staff(self, value):
        if StaffPayroll.objects.filter(staff=value).exists():
            raise serializers.ValidationError("Staff payroll already exists.")
        return value

    def create(self, validated_data):

        payroll = super().create(validated_data)
        try:
            onboarding_progress = StaffOnboardingProgress.objects.get(
                staff=payroll.staff
            )
            onboarding_progress.payroll_setup_completed = True
            onboarding_progress.save()
        except StaffOnboardingProgress.DoesNotExist:
            pass

        return payroll


class StaffPayrollListSerializer(StaffPayrollCreateSerializer):
    staff = StaffListDetailSerializer()

    class Meta:
        model = StaffPayroll
        fields = [
            "id",
            "staff",
            "basic_salary",
            "house_allowance",
            "transport_allowance",
            "other_allowances",
            "nssf_number",
            "nhif_number",
            "kra_pin",
            "bank_name",
            "bank_account_number",
            "mpesa_number",
            "payment_frequency",
            "created_on",
            "updated_on",
        ]


class StaffPaySlipSerializer(serializers.ModelSerializer):
    staff = StaffListDetailSerializer()

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
        ]


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
        fields = ['staff', 'year', 'total_days', 'used_days']
        extra_kwargs = {
            'total_days': {'required': True},
            'used_days': {'required': False},
            'staff': {'required': False},
        }
        
    def validate_staff(self, value):
        """Ensure staff exists and is active"""
        if not Staff.objects.filter(id=value.id, status='Active').exists():
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
        used_days = attrs.get('used_days', 0)
        total_days = attrs.get('total_days')
        
        if used_days > total_days:
            raise serializers.ValidationError(
                "Used days cannot exceed total days"
            )
        return attrs
    
class StaffLeaveEntitlementDetailSerializer(serializers.ModelSerializer):
    """Serializer for listing staff leave entitlement details""" 
    staff = StaffListDetailSerializer()
    remaining_days = serializers.ReadOnlyField()
    class Meta:
        model = StaffLeaveEntitlement
        fields = [
            'id',
            'staff',
            'year',
            'total_days',
            'used_days',
            'remaining_days',
        ]
    
   