from django.shortcuts import render
from rest_framework import generics, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from apps.core.base_api_error_exceptions.base_exceptions import CustomAPIException
from apps.schools.models import Semester
from apps.student_finance.filters import (
    StudentFeeInvoiceFilter,
    StudentFeeLedgerFilter,
    StudentFeePaymentFilter,
    StudentFeeStatementFilter,
)
from django.db.models import OuterRef, Subquery

from apps.student_finance.models import (
    InvoiceType,
    StudentFeeInvoice,
    StudentFeePayment,
    StudentFeeLedger,
    StudentFeeStatement,
)
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from apps.student_finance.serializers import (
    AllFeeStatementListSerializer,
    CreateAndUpdateInvoiceTypeSerializer,
    FeeLedgeListSerializer,
    InvoiceTypeListSerializer,
    StudentFeeInvoiceListSerializer,
    StudentFeePaymentListSerializer,
    StudentFeeLedgerSerializer,
    StudentFeePaymentSerializer,
    StudentFeeStatementListSerializer,
)
from apps.students.models import Student
from decimal import Decimal
from django.db.models import Sum, Count, Q

from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated


class StudentFeeInvoiceListView(generics.ListAPIView):
    queryset = StudentFeeInvoice.objects.all().order_by("-created_on")
    serializer_class = StudentFeeInvoiceListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StudentFeeInvoiceFilter
    permission_classes = [IsAuthenticated]

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


class StudentFeeStatementListView(generics.ListAPIView):
    serializer_class = StudentFeeStatementListSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        semester_id = self.request.query_params.get("semester")
        student_id = self.request.query_params.get("student")

        if not semester_id or not student_id:
            raise ValidationError(
                {
                    "detail": "Both 'semester' and 'student' query parameters are required."
                }
            )

        return StudentFeeStatement.objects.filter(
            semester_id=semester_id, student_id=student_id
        )
class FeeStatementsView(generics.ListAPIView):
    serializer_class = AllFeeStatementListSerializer
    queryset = StudentFeeStatement.objects.all().order_by("-created_on")
    filter_backends = [DjangoFilterBackend]
    filterset_class = StudentFeeStatementFilter
    # For Postgres support
    # def get_queryset(self):
    #     return StudentFeeStatement.objects.order_by(
    #         "student_id", "-created_on"
    #     ).distinct("student_id")

    
    def get_queryset(self):
        # Subquery to get latest statement per student
        latest_statement_subquery = StudentFeeStatement.objects.filter(
            student_id=OuterRef('student_id')
        ).order_by('-created_on').values('pk')[:1]

        return StudentFeeStatement.objects.filter(
            pk__in=Subquery(latest_statement_subquery)
        ).order_by('-created_on')

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
                paginated_fee_ledger_qs = paginator.paginate_queryset(
                    fee_ledger_qs, request
                )
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
    permission_classes = [IsAuthenticated]

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
                paginated_payments_qs = paginator.paginate_queryset(
                    payments_qs, request
                )
                serializer = self.get_serializer(paginated_payments_qs, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(payments_qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TotalCollectedFeesView(APIView):
    """
    Get total fees collected, optionally filtered by semester.
    Uses StudentFeeStatement as the primary source for financial data.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        semester_id = request.query_params.get("semester")
        semester = None

        if not semester_id:
            semester = Semester.objects.filter(status="Active").first()
            if semester:
                semester_id = semester.id
        else:
            try:
                semester = Semester.objects.get(id=semester_id)
            except Semester.DoesNotExist:
                return Response(
                    {"error": "Semester not found"}, status=status.HTTP_404_NOT_FOUND
                )

        statement_queryset = StudentFeeStatement.objects.filter(
            statement_type="Payment"
        )
        if semester_id:
            statement_queryset = statement_queryset.filter(semester_id=semester_id)

        total_collected = statement_queryset.aggregate(total_collected=Sum("credit"))[
            "total_collected"
        ] or Decimal("0.00")

        payment_method_totals = (
            statement_queryset.values("payment_method")
            .annotate(total=Sum("credit"), count=Count("id"))
            .order_by("payment_method")
        )

        total_invoiced = Decimal("0.00")
        if semester_id:
            invoiced_queryset = StudentFeeStatement.objects.filter(
                statement_type="Invoice", semester_id=semester_id
            )
            total_invoiced = invoiced_queryset.aggregate(total_invoiced=Sum("debit"))[
                "total_invoiced"
            ] or Decimal("0.00")

        collection_rate = Decimal("0.00")
        if total_invoiced > 0:
            collection_rate = (total_collected / total_invoiced * 100).quantize(
                Decimal("0.01")
            )

        semester_info = None
        if semester:
            semester_info = {
                "id": semester.id,
                "name": semester.name,
                "academic_year": (
                    semester.academic_year
                    if hasattr(semester, "academic_year")
                    else None
                ),
                "status": semester.status,
            }

        return Response(
            {
                "total_collected": total_collected,
                "total_invoiced": total_invoiced,
                "collection_rate_percentage": collection_rate,
                "by_payment_method": list(payment_method_totals),
                "semester": semester_info,
                "payment_count": sum(
                    method["count"] for method in payment_method_totals
                ),
            },
            status=status.HTTP_200_OK,
        )


class CreateInvoiceTypeView(generics.CreateAPIView):
    queryset = InvoiceType.objects.all()
    serializer_class = CreateAndUpdateInvoiceTypeSerializer

    def create(self, request, *args, **kwargs):
        try:
            name = request.data.get("name")
            if InvoiceType.objects.filter(name__iexact=name).exists():
                return Response(
                    {
                        "success": False,
                        "error": "InvoiceType with this name already exists.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return super().create(request, *args, **kwargs)
        except Exception as exc:
            # logger.error(f"Error creating InvoiceType: {exc}")
            return Response(
                {"success": False, "error": f"Internal server error: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class InvoiceTypesListView(generics.ListAPIView):
    serializer_class = InvoiceTypeListSerializer
    queryset = InvoiceType.objects.all().order_by("-created_on")

    def get(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            qs = self.filter_queryset(qs)
            page = request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_qs = paginator.paginate_queryset(qs, request)
                serializer = self.get_serializer(paginated_qs, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            # logger.error(f"Error listing InvoiceTypes: {str(e)}")
            return Response(
                {"success": False, "error": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class InvoiceTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CreateAndUpdateInvoiceTypeSerializer
    queryset = InvoiceType.objects.all()
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            name = request.data.get("name")
            if (
                name
                and InvoiceType.objects.exclude(id=instance.id)
                .filter(name__iexact=name)
                .exists()
            ):
                return Response(
                    {
                        "success": False,
                        "error": "Another InvoiceType with this name already exists.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return super().update(request, *args, **kwargs)
        except Exception as exc:
            # logger.error(f"Error updating InvoiceType: {exc}")
            return Response(
                {"success": False, "error": f"Internal server error: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
