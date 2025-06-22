from rest_framework import serializers
from apps.schools.serializers import SemesterListSerializer
from apps.student_finance.models import (
    StudentFeeLedger,
    StudentFeeInvoice,
    StudentFeePayment,
    StudentFeeStatement,
)


class StudentFeeLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeeLedger
        fields = "__all__"


class StudentFeeInvoiceListSerializer(serializers.ModelSerializer):
    student_name  = serializers.SerializerMethodField()
    student_reg_no = serializers.SerializerMethodField()
    semester = SemesterListSerializer()
    bal_due = serializers.ReadOnlyField()
    class Meta:
        model = StudentFeeInvoice
        fields = [
            "id",
            "amount",
            "amount_paid",
            "description",
            "reference",
            "bal_due",
            "semester",
            "student_name",
            "student_reg_no",
            "student_id",
            "created_on",
            "updated_on",
            "status",
            

        ]
    def get_student_name(self, obj):
        return obj.student.name()
    def get_student_reg_no(self, obj):
        return obj.student.registration_number


class StudentFeePaymentListSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_reg_no = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentFeePayment
        fields = [
            "id",
            "amount",
            "payment_date",
            "payment_method",
            "created_on",
            "updated_on",
            "student_name",
            "student_reg_no"
        ]
    def get_student_name(self, obj):
        return obj.student.name()
    def get_student_reg_no(self, obj):
        return obj.student.registration_number

class StudentFeeStatementListSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_reg_no = serializers.SerializerMethodField()
    class Meta:
        model = StudentFeeStatement
        fields = [
            "id",
            "balance",
            "credit",
            "debit",
            "semester",
            "statement_type",
            "student_name",
        ]
    def get_student_name(self, obj):
        return obj.student.name()
    def get_student_reg_no(self, obj):
        return obj.student.registration_number
class  FeeLedgeListSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_reg_no = serializers.SerializerMethodField()
    class Meta:
        model = StudentFeeLedger
        fields = [
            "id",
            "balance",
            "credit",
            "debit",
            "student_name",
            "student_reg_no",
            "transaction_type",
        ]
    def get_student_name(self, obj):
        return obj.student.name()
    def get_student_reg_no(self, obj):
        return obj.student.registration_number

class StudentFeePaymentSerializer(serializers.Serializer):
    student = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=["Mpesa", "Cash", "Bank Transfer"])
    semester = serializers.IntegerField(required=False) 
    
    
