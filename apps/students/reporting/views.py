from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from apps.schools.models import ProgrammeCohort, Semester

from apps.students.mixins.SemesterReportingMixin import SemesterReportingMixin
from apps.students.reporting.filters import SemesterReportingFilter
from apps.students.reporting.serializers import (
    GraduateSingleStudentSerializer,
    GraduateStudentsSerializer,
    PromoteSingleStudentSerializer,
    PromoteStudentsSerializer,
    PromotionListSerializer,
    ReportSemesterStudentsSerializer,
    ReportSingleSemesterStudentSerializer,
    SemesterReportingListSerializer,
    StudentCourseEnrollmentSerializer,
)
from apps.students.models import Promotion, SemesterReporting, Student, StudentCourseEnrollment
from apps.finance.models import FeeStructure
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated



from services.constants import ALL_STAFF_ROLES
from services.permissions import HasUserRole
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

class ReportSemesterStudentsView(SemesterReportingMixin, generics.CreateAPIView):
    """Bulk semester reporting by cohort"""
    serializer_class = ReportSemesterStudentsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cohort = serializer.validated_data["cohort"]
        semester = serializer.validated_data["semester"]
        done_by = request.user if request.user.is_authenticated else None
        reports = self.report_semester_students(cohort, semester, done_by)
        return Response(
            {
                "message": f"{len(reports['new_reports'])} new, {len(reports['duplicates'])} duplicates",
                "new_reports_count": len(reports["new_reports"]),
                "duplicates_count": len(reports["duplicates"]),
            },
            status=status.HTTP_200_OK,
        )


class ReportSingleSemesterStudentView(SemesterReportingMixin, generics.CreateAPIView):
    """Single semester reporting by registration_number"""
    serializer_class = ReportSingleSemesterStudentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reg_number = serializer.validated_data["registration_number"]
        semester = serializer.validated_data["semester"]
        done_by = request.user if request.user.is_authenticated else None

        try:
            student = Student.objects.get(registration_number=reg_number)
        except Student.DoesNotExist:
            return Response({"error": f"Student with reg no {reg_number} not found"}, status=400)

        self.report_semester_student(student, semester, done_by)
        return Response({"message": f"{student} reported to {semester}"}, status=200)


class PromoteStudentsView(SemesterReportingMixin, generics.CreateAPIView):
    """Promote cohort to new study year"""
    serializer_class = PromoteStudentsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cohort = serializer.validated_data["cohort"]
        study_year = serializer.validated_data["study_year"]
        done_by = request.user if request.user.is_authenticated else None
        count = self.promote_students(cohort, study_year, done_by)
        return Response({"message": f"{count} students promoted"}, status=200)


class SemesterReportingListAPIView(generics.ListAPIView):
    queryset = SemesterReporting.objects.all().order_by("-created_on")
    serializer_class = SemesterReportingListSerializer

class PromotionsListAPIView(generics.ListAPIView):
    queryset = Promotion.objects.all().order_by("-created_on")
    serializer_class = PromotionListSerializer



class GraduateStudentsView(SemesterReportingMixin, generics.CreateAPIView):
    """Graduate all students in a given cohort"""
    serializer_class = GraduateStudentsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cohort = serializer.validated_data["cohort"]
        done_by = request.user if request.user.is_authenticated else None
        count = self.graduate_students(cohort, done_by)
        return Response(
            {"message": f"{count} students graduated"},
            status=status.HTTP_200_OK,
        )

class GraduateSingleStudentView(SemesterReportingMixin, generics.CreateAPIView):
    """Graduate a single student by registration number"""
    serializer_class = GraduateSingleStudentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reg_number = serializer.validated_data["registration_number"]
        done_by = request.user if request.user.is_authenticated else None

        try:
            student = Student.objects.get(registration_number=reg_number)
        except Student.DoesNotExist:
            return Response(
                {"error": f"Student with registration number {reg_number} not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if student.status == "Graduated":
            return Response(
                {"error": f"{student.name()} ({reg_number}) is already graduated."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.graduate_student(student, done_by)

        return Response(
            {"message": f"{student.name()} ({reg_number}) has been graduated."},
            status=status.HTTP_200_OK,
        )

class PromoteSingleStudentView(SemesterReportingMixin, generics.CreateAPIView):
    """Promote a single student to a new study year by registration number"""
    serializer_class = PromoteSingleStudentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reg_number = serializer.validated_data["registration_number"]
        study_year = serializer.validated_data["study_year"]
        done_by = request.user if request.user.is_authenticated else None

        try:
            student = Student.objects.get(registration_number=reg_number)
        except Student.DoesNotExist:
            return Response(
                {"error": f"Student with registration number {reg_number} not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.promote_student(student, study_year, done_by)

        return Response(
            {"message": f"{student.name()} ({reg_number}) promoted to {study_year.name}."},
            status=status.HTTP_200_OK,
        )


### Units Registration API View
class SemesterReportingCreateView(generics.CreateAPIView):
    queryset = StudentCourseEnrollment.objects.all()
    serializer_class = StudentCourseEnrollmentSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            reporting = serializer.save()
            reporting.academic_year = reporting.semester.study_year
            reporting.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
