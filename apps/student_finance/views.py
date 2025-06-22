from django.shortcuts import render
from rest_framework import generics, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from apps.core.base_api_error_exceptions.base_exceptions import CustomAPIException
from apps.schools.models import Semester
from apps.student_finance.filters import StudentFeeInvoiceFilter, StudentFeeLedgerFilter, StudentFeePaymentFilter
from apps.student_finance.mixins import StudentInvoicingMixin
from apps.student_finance.models import (
    StudentFeeInvoice,
    StudentFeePayment,
    StudentFeeLedger,
)
from rest_framework.views import APIView
from apps.student_finance.serializers import (
    FeeLedgeListSerializer,
    StudentFeeInvoiceListSerializer,
    StudentFeePaymentListSerializer,
    StudentFeeLedgerSerializer,
    StudentFeePaymentSerializer,
)
from apps.students.models import Student




class StudentFeeInvoiceListView(generics.ListAPIView):
    queryset = StudentFeeInvoice.objects.all().order_by("-created_on")
    serializer_class = StudentFeeInvoiceListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StudentFeeInvoiceFilter
    
    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            invoices = self.get_queryset()
            invoices = self.filter_queryset(invoices)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_invoices = paginator.paginate_queryset(invoices, request)
                serializer = self.get_serializer(paginated_invoices, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(invoices, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class StudentFeeLedgerListView(generics.ListAPIView):
    queryset = StudentFeeLedger.objects.all().order_by("-created_on")
    serializer_class = FeeLedgeListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StudentFeeLedgerFilter
    
    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            fee_ledger_qs = self.get_queryset()
            fee_ledger_qs = self.filter_queryset(fee_ledger_qs)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_fee_ledger_qs = paginator.paginate_queryset(fee_ledger_qs, request)
                serializer = self.get_serializer(paginated_fee_ledger_qs, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(fee_ledger_qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StudentFeeInvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentFeeInvoice.objects.all()
    serializer_class = StudentFeeInvoiceListSerializer
    lookup_field = "pk"


class StudentFeePaymentListView(generics.ListAPIView):
    queryset = StudentFeePayment.objects.all()
    serializer_class = StudentFeePaymentListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StudentFeePaymentFilter
    
    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            payments_qs = self.get_queryset()
            payments_qs = self.filter_queryset(payments_qs)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_payments_qs = paginator.paginate_queryset(payments_qs, request)
                serializer = self.get_serializer(paginated_payments_qs, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(payments_qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class StudentFeePaymentView(APIView):
    def post(self, request):
        serializer = StudentFeePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        print("data", data)
        try:
            student = Student.objects.get(id=data["student"])
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        semester = None
        if "semester" in data:
            semester = Semester.objects.filter(id=data["semester"]).first()

        success = StudentInvoicingMixin(
            student=student,
            transaction_type="Student Payment",
            amount=data["amount"],
            payment_method=data["payment_method"],
            semester=semester
        ).run()

        if success:
            return Response({"message": "Payment processed successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Payment failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)