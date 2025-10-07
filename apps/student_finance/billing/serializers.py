from decimal import Decimal
from rest_framework import serializers
from apps.students.models import Student
from apps.schools.models import ProgrammeCohort, Semester
from apps.student_finance.models import InvoiceType, StudentFeeStatement

class SingleFeeInvoiceSerializer(serializers.Serializer):
    registration_number = serializers.CharField()
    semester = serializers.PrimaryKeyRelatedField(queryset=Semester.objects.all())
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    

class BulkFeeInvoiceSerializer(serializers.Serializer):
    semester = serializers.PrimaryKeyRelatedField(queryset=Semester.objects.all())
    cohort = serializers.PrimaryKeyRelatedField(queryset=ProgrammeCohort.objects.all())
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

class FeePaymentSerializer(serializers.Serializer):
    registration_number = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=[("Mpesa","Mpesa"),("Bank Transfer","Bank Transfer"),("Cash","Cash")])
    semester = serializers.PrimaryKeyRelatedField(queryset=Semester.objects.all(), required=False, allow_null=True)
    reference = serializers.CharField(required=False, allow_blank=True)





class BulkInvoiceSerializer(serializers.Serializer):
    semester = serializers.PrimaryKeyRelatedField(queryset=Semester.objects.all())
    cohort = serializers.PrimaryKeyRelatedField(queryset=ProgrammeCohort.objects.all())
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    invoice_type = serializers.PrimaryKeyRelatedField(
        queryset=InvoiceType.objects.all(), required=False
    )


class SingleInvoiceSerializer(serializers.Serializer):
    admission_number = serializers.CharField(required=True)
    semester = serializers.PrimaryKeyRelatedField(queryset=Semester.objects.all())
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    invoice_type = serializers.PrimaryKeyRelatedField(
        queryset=InvoiceType.objects.all(), required=True
    )

class FeeStatementDetailSerializer(serializers.ModelSerializer):
    semester = serializers.StringRelatedField()
    class Meta:
        model = StudentFeeStatement
        fields = [
            "reference",
            "statement_type",
            "debit",
            "credit",
            "balance",
            "payment_method",
            "semester",
            "created_on",
        ]

class StudentFeeStatementsSerializer(serializers.ModelSerializer):
    statements = FeeStatementDetailSerializer(source="fee_statements", many=True)
    programme = serializers.StringRelatedField()
    cohort = serializers.StringRelatedField()
    balance = serializers.SerializerMethodField()
    class Meta:
        model = Student
        fields = [
            "id",
            "registration_number",
            "name",
            "programme",
            "cohort",
            "balance",
            "statements",
        ]
        
    def get_balance(self, obj):
        """
            Compute current balance from the student's statements.
            If none, return "0.00"
        """
        fee_statements = getattr(obj, "fee_statements", [])
        if not fee_statements:
            return "0.00"

        # Take the last statement balance, or compute manually
        latest_balance = fee_statements.order_by("-created_on").first().balance
        return str(latest_balance or Decimal("0.00"))
        # manual computing
        # def get_balance(self, obj):
        #     fee_statements = getattr(obj, "fee_statements", [])
        #     if not fee_statements:
        #         return "0.00"

        #     total_debit = sum(Decimal(fs.debit) for fs in fee_statements)
        #     total_credit = sum(Decimal(fs.credit) for fs in fee_statements)
        #     return str(total_debit - total_credit)
