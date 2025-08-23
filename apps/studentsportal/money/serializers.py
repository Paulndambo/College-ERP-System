from rest_framework import serializers

from apps.student_finance.models import (
    StudentFeePayment, StudentFeeInvoice, StudentFeeLedger, StudentFeeStatement
)


############ Fees Related Serializers ############
class StudentFeeInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeeInvoice
        fields = '__all__'


class StudentFeeLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeeLedger
        fields = '__all__'


class StudentFeeStatementSerializer(serializers.ModelSerializer):
    semester_name = serializers.SerializerMethodField()
    academic_year = serializers.CharField(source='semester.academic_year', read_only=True)
    class Meta:
        model = StudentFeeStatement
        fields = '__all__'

    def get_semester_name(self, obj):
        return f"{obj.semester.name} {obj.semester.academic_year}" if obj.semester else None

class StudentFeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeePayment
        fields = '__all__'


