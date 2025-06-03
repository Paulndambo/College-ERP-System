from django.shortcuts import render
from rest_framework import generics, status

from apps.student_finance.models import StudentFeeInvoice, StudentFeePayment, StudentFeeLedger
from apps.student_finance.serializers import StudentFeeInvoiceSerializer, StudentFeePaymentSerializer, StudentFeeLedgerSerializer

# Create your views here.
class StudentFeeLedgerListView(generics.ListCreateAPIView):
    queryset = StudentFeeLedger.objects.all()
    serializer_class = StudentFeeLedgerSerializer
    
    
class StudentFeeLedgerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentFeeLedger.objects.all()
    serializer_class = StudentFeeLedgerSerializer
    
    lookup_field = "pk"


class StudentFeeInvoiceListView(generics.ListCreateAPIView):
    queryset = StudentFeeInvoice.objects.all()
    serializer_class = StudentFeeInvoiceSerializer
    
    
class StudentFeeInvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentFeeInvoice.objects.all()
    serializer_class = StudentFeeInvoiceSerializer
    
    lookup_field = "pk"
    

class StudentFeePaymentListView(generics.ListCreateAPIView):
    queryset = StudentFeePayment.objects.all()
    serializer_class = StudentFeePaymentSerializer
    

class StudentFeePaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentFeePayment.objects.all()
    serializer_class = StudentFeePaymentSerializer
    
    lookup_field = "pk"