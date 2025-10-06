from django.shortcuts import render


from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics

from apps.students.models import (
    Student,
    StudentAttendance,
    StudentDocument,
    MealCard,
    StudentProgramme,
    StudentCheckIn,
    SemesterReporting,
)
from apps.student_finance.models import (
    StudentFeeInvoice,
    StudentFeePayment,
    StudentFeeLedger,
    StudentFeeStatement,
)

from apps.exams.models import ExamData
from apps.library.models import Fine, Member, BorrowTransaction

from apps.studentsportal.money.serializers import (
    StudentFeePaymentSerializer,
    StudentFeeInvoiceSerializer,
    StudentFeeLedgerSerializer,
    StudentFeeStatementSerializer,
)


# Create your views here.
class StudentFeesPaymentsAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentFeePaymentSerializer

    def get_queryset(self):
        student = Student.objects.get(user=self.request.user)
        return StudentFeePayment.objects.filter(student=student)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentFeeInvoicesAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentFeeInvoiceSerializer

    def get_queryset(self):
        student = Student.objects.get(user=self.request.user)
        return StudentFeeInvoice.objects.filter(student=student)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentFeeLedgerAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentFeeLedgerSerializer

    def get_queryset(self):
        student = Student.objects.get(user=self.request.user)
        return StudentFeeLedger.objects.filter(student=student)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentFeeStatementAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentFeeStatementSerializer

    def get_queryset(self):
        student = Student.objects.get(user=self.request.user)
        return StudentFeeStatement.objects.filter(student=student)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
