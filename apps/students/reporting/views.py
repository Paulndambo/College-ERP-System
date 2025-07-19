from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from apps.schools.models import ProgrammeCohort, Semester
from apps.students.reporting.filters import SemesterReportingFilter
from apps.students.reporting.serializers import (
    SemesterReportingListSerializer,
    SemesterReportingSerializer,
)
from apps.students.models import SemesterReporting
from apps.finance.models import FeeStructure

from apps.student_finance.mixins import StudentInvoicingMixin
from apps.students.reporting.usecases.promote_students import (
    promote_students_to_next_semester,
)
from apps.students.reporting.usecases.reporting_service import SemesterReportingService
from services.constants import ALL_STAFF_ROLES
from services.permissions import HasUserRole
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

"""By Paul - Semester Reporting API View"""
# class SemesterReportingAPIView(generics.ListCreateAPIView):
#     queryset = SemesterReporting.objects.all()
#     serializer_class = SemesterReportingSerializer

#     @transaction.atomic
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)

#         if serializer.is_valid(raise_exception=True):
#             reporting = serializer.save()

#             fee_structure = FeeStructure.objects.filter(
#                 programme=reporting.student.programme,
#                 semester__name=reporting.semester.name,
#             ).first()

#             if not fee_structure:
#                 return Response(
#                     {
#                         "message": "No fee structure found for this programme and semester"
#                     },
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#             semester_total_fees = fee_structure.total_amount()

#             success = StudentInvoicingMixin(
#                 student=reporting.student,
#                 semester=reporting.semester,
#                 transaction_type="Standard Invoice",
#                 amount=semester_total_fees,
#             ).run()
#             print("**********Success***********")
#             print(success)
#             print("**********Success***********")
#             if success == True:
#                 return Response(
#                     {"message": "Student invoice created successfully"},
#                     status=status.HTTP_201_CREATED,
#                 )
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SemesterReportingAPIView(APIView):
    """
    Handles both individual student semester reporting and cohort promotion
    with automatic fee structure invoicing
    """

    def post(self, request, cohort_id=None):
        """Handle POST requests for both individual and cohort reporting"""
        if cohort_id:

            cohort = get_object_or_404(ProgrammeCohort, pk=cohort_id)

            next_semester_id = request.data.get("semester")
            if not next_semester_id:
                return Response(
                    {"error": "next semester is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            next_semester = get_object_or_404(Semester, pk=next_semester_id)
            print("next_semester", next_semester)
            print("cohort", cohort)
            success, response_data, status_code = (
                SemesterReportingService.handle_cohort_promotion(cohort, next_semester)
            )
        else:
            semester_id = request.data.get("semester")
            if not semester_id:
                return Response(
                    {"error": "semester is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            semester = get_object_or_404(Semester, pk=semester_id)
            success, response_data, status_code = (
                SemesterReportingService.handle_individual_reporting(
                    semester, request.data
                )
            )

        return Response(response_data, status=status_code)


class SemisterReportingList(generics.ListAPIView):
    queryset = SemesterReporting.objects.all().order_by("-created_on")
    serializer_class = SemesterReportingListSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = SemesterReportingFilter

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            reporting_qs = self.get_queryset()
            reporting_qs = self.filter_queryset(reporting_qs)

            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_reporting_qs = paginator.paginate_queryset(
                    reporting_qs, request
                )
                serializer = self.get_serializer(paginated_reporting_qs, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(reporting_qs, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
