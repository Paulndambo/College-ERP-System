from rest_framework import serializers
from apps.student_finance.models import StudentFeeLedger, StudentFeeInvoice, StudentFeePayment


class StudentFeeLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeeLedger
        fields = "__all__"
        
        
class StudentFeeInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeeInvoice
        fields = "__all__"
        
class StudentFeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFeePayment
        fields = "__all__"