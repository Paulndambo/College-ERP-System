import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.db import transaction

from apps.schools.models import Semester
from apps.student_finance.mixins.BillingMixin import StudentInvoicingMixin
from apps.student_finance.models import InvoiceType,StudentFeeInvoice, StudentFeeStatement
from apps.student_finance.billing.serializers import BulkFeeInvoiceSerializer, BulkInvoiceSerializer, FeePaymentSerializer, SingleFeeInvoiceSerializer, SingleInvoiceSerializer, StudentFeeStatementsSerializer
from apps.students.models import Student
from decimal import Decimal

logger = logging.getLogger(__name__)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from django.shortcuts import get_object_or_404

class BulkFeeInvoiceView(generics.CreateAPIView):
    """Generate invoices for all students in a class level (from FeeStructure)."""

    serializer_class = BulkFeeInvoiceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cohort = serializer.validated_data["cohort"]
        semester = serializer.validated_data["semester"]
        try:
            invoice_type = InvoiceType.objects.get(is_fee_type=True, is_active=True)
        except InvoiceType.DoesNotExist:
            return Response(
                {"error": "No active fee type invoice type found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        mixin = StudentInvoicingMixin(
            cohort=cohort,
            semester=semester,
            invoice_type=invoice_type,
            user=request.user,
            action="invoice",
        )
        try:
            invoices = mixin._process()
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if invoices is None:
            return Response(
                {"error": "Fee structure missing or other fatal error."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(invoices) == 0:
            return Response(
                {
                    "message": "No new fee invoices created. All students were already invoiced for fees  "
                            f"for {semester.name} - {semester.academic_year.name}.",
                    "invoices": [],
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": f"{len(invoices)} invoices created",
                "invoices": [inv.reference for inv in invoices],
            },
            status=status.HTTP_201_CREATED,
        )


class SingleStudentFeeInvoiceView(generics.CreateAPIView):
    """Generate an invoice for a single student (from FeeStructure)."""

    serializer_class = SingleFeeInvoiceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        adm_no = serializer.validated_data["registration_number"]
        student = Student.objects.get(registration_number=adm_no)

        print("student", student)
        # student = serializer.validated_data["registration_number"]
        semester = serializer.validated_data["semester"]
        # invoice_type = serializer.validated_data["invoice_type"]
        try:
            invoice_type = InvoiceType.objects.get(is_fee_type=True, is_active=True)
        except InvoiceType.DoesNotExist:
            return Response(
                {
                    "error": "No active fee type invoice type found. Create one or update an existing one by ticking is_fee checkbox."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        if StudentFeeInvoice.objects.filter(
            student=student, semester=semester, invoice_type=invoice_type
        ).exists():
            return Response(
                {
                    "error": f"A Fee invoice for {student} already exists "
                             f"for {semester.name} - {semester.academic_year.year}."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        mixin = StudentInvoicingMixin(
            student=student,
            semester=semester,
            invoice_type=invoice_type,
            user=request.user,
            action="invoice",
        )
        print("student", student.cohort)
        try:
            invoice = mixin._process()
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if not invoice:
            return Response(
                {
                    "error": (
                        f"No applicable fee structure found for student's class "
                        f"'{student.cohort.name} {student.cohort.semester.academic_year.name}' in '{student.cohort.semester.semester} - {student.cohort.semester.academic_year.year}'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "message": "Invoice created",
                "invoice_ref": invoice.reference,
                "student": student.id,
                "semester": semester.id,
                "amount": str(invoice.amount),
            },
            status=status.HTTP_201_CREATED,
        )


class SingleInvoiceView(generics.CreateAPIView):
    """Create an ad-hoc invoice for a single student (amount must be provided)."""

    serializer_class = SingleInvoiceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # student = serializer.validated_data["registration_number"]
        adm_no = request.data.get("registration_number")
        student = Student.objects.get(registration_number=adm_no)
        semester = serializer.validated_data["semester"]
        invoice_type = serializer.validated_data["invoice_type"]
        amount = serializer.validated_data.get("amount")
        cohort = student.cohort
        print("student", student)
        print("class", cohort)
        mixin = StudentInvoicingMixin(
            student=student,
            semester=semester,
            invoice_type=invoice_type,
            # cohort=cohort,
            amount=Decimal(amount),
            user=request.user,
            action="invoice",
        )
        invoice = mixin._process()

        return Response(
            {
                "message": "Invoice created",
                "invoice_ref": invoice.reference,
                "student": student.id,
                "amount": str(invoice.amount),
                "type": invoice_type.name,
            },
            status=status.HTTP_201_CREATED,
        )


class BulkInvoiceView(generics.CreateAPIView):
    """Create ad-hoc invoices for all students in a class level (amount required)."""

    serializer_class = BulkInvoiceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cohort = serializer.validated_data["cohort"]
        semester = serializer.validated_data["semester"]
        invoice_type = serializer.validated_data["invoice_type"]
        amount = serializer.validated_data["amount"]

        mixin = StudentInvoicingMixin(
            cohort=cohort,
            semester=semester,
            invoice_type=invoice_type,
            amount=Decimal(amount),
            user=request.user,
            action="invoice",
        )
        invoices = mixin._process()

        return Response(
            {
                "message": f"{len(invoices)} Invoices created",
                "invoices": [inv.reference for inv in invoices],
            },
            status=status.HTTP_201_CREATED,
        )



class FeePaymentView(generics.CreateAPIView, StudentInvoicingMixin):
    """Endpoint for processing student payments"""

    serializer_class = FeePaymentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        registration_number = serializer.validated_data.get("registration_number")
        student = Student.objects.filter(registration_number=registration_number).first()

        if not student:
            return Response(
                {
                    "error": f"Student not found with given registration number {registration_number}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Pick term
        semester = serializer.validated_data.get("semester")
        if not semester:
            semester = Semester.objects.filter(is_active=True).first()

        # Set mixin state
        self.student = student
        self.semester = semester
        self.amount = serializer.validated_data["amount"]
        self.payment_method = serializer.validated_data["payment_method"]
        # self.description = serializer.validated_data["description"]
        self.reference = serializer.validated_data["reference"]
        self.user = self.request.user
        self.action = "payment"

        # Process payment
        payment = self._process()

        result = {
            "message": "Payment processed successfully",
            "reference": payment.reference,
            "student": payment.student.registration_number,
            "amount": str(payment.amount),
            "method": payment.payment_method,
        }

        return Response(result, status=status.HTTP_201_CREATED)


class FeeStatementReportsAPIView(APIView):
    permission_classes = []

    """
    Returns fee statement data by:
    - registration_number + semester_id + optional academic_year
    - OR cohort_id + semester_id + optional academic_year
    """

    def get(self, request):
        registration_number = request.query_params.get("registration_number")
        cohort_id = request.query_params.get("cohort")
        semester_id = request.query_params.get("semester")
        academic_year = request.query_params.get("academic_year")  # optional filter

        if not (registration_number or cohort_id):
            return Response(
                {"error": "Provide either registration_number or cohort"},
                status=400,
            )


        semester = None
        if semester_id:
            semester = get_object_or_404(Semester, id=semester_id)

        if registration_number:
            return self.process_single_statement(registration_number, semester, academic_year)

        elif cohort_id:
            return self.process_bulk_statement(cohort_id, semester, academic_year)

        return Response(
            {"error": "Provide either registration number or cohort and semester or academic year"}, status=400
        )

    def process_single_statement(self, registration_number, semester, academic_year):
        try:
            student = Student.objects.filter(registration_number=registration_number).first()
            if not student:
                return Response(
                    {"error": f"Student with registration {registration_number} does not exist"},
                    status=404
                )

            qs = StudentFeeStatement.objects.filter(student=student)

            if semester:
                qs = qs.filter(semester=semester)

            if academic_year:
                qs = qs.filter(semester__academic_year=academic_year)

            qs = qs.order_by("-created_on")
            student.fee_statements = qs

            serializer = StudentFeeStatementsSerializer(student)
            return Response([serializer.data], status=200)

        except Exception as e:
            logger.error(f"Error fetching statement for {registration_number}: {e}")
            return Response({"error": "Error fetching student fee statement"}, status=500)


    def process_bulk_statement(self, cohort_id, semester, academic_year):
        try:
            students = Student.objects.filter(cohort_id=cohort_id)
            if not students.exists():
                return Response({"error": "No students found in this cohort"}, status=404)

            results = []
            for student in students:
                qs = StudentFeeStatement.objects.filter(student=student)

                if semester:
                    qs = qs.filter(semester=semester)

                if academic_year:
                    qs = qs.filter(semester__academic_year=academic_year)

                qs = qs.order_by("-created_on")

                if qs.exists():
                    student.fee_statements = qs
                    results.append(student)

            serializer = StudentFeeStatementsSerializer(results, many=True)
            return Response(serializer.data, status=200)

        except Exception as e:
            logger.error(f"Error fetching cohort statements: {e}")
            return Response({"error": "Error fetching cohort fee statements"}, status=500)
