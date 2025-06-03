from django.db import transaction
from rest_framework.response import Response
from rest_framework import status, generics

from apps.students.reporting.serializers import SemesterReportingSerializer
from apps.students.models import SemesterReporting
from apps.finance.models import FeeStructure

from apps.student_finance.mixins import StudentInvoicingMixin

class SemesterReportingAPIView(generics.ListCreateAPIView):
    queryset = SemesterReporting.objects.all()
    serializer_class = SemesterReportingSerializer

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            reporting = serializer.save()
            
            fee_structure = FeeStructure.objects.filter(programme=reporting.programme, semester__name=reporting.semester.name).first()
            
            if not fee_structure:
                return Response({"message": "No fee structure found for this programme and semester"}, status=status.HTTP_404_NOT_FOUND)
            
            semester_total_fees = fee_structure.total_amount()
            
            success = StudentInvoicingMixin(
                student=reporting.student,
                semester=reporting.semester,
                transaction_type="Standard Invoice",
                amount=semester_total_fees,    
            ).run()
            
            if success == True:
                return Response({"message": "Student invoice created successfully"}, status=status.HTTP_201_CREATED)
            return Response({"failed": "Student invoice creation failed"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
