from apps.admissions.admissions_utils import generate_registration_number
from apps.core.models import Campus, UserRole
from apps.schools.models import ProgrammeCohort
from apps.students.models import Student, StudentDocument, StudentEducationHistory
from apps.students.serializers import StudentCreateSerializer, StudentListSerializer
from apps.users.models import User
from .filters import EnrollmentsByIntakeFilter, IntakeFilter, StudentApplicationFilter
from apps.core.base_api_error_exceptions.base_exceptions import CustomAPIException
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from services.constants import ALL_ROLES, ALL_STAFF_ROLES, ROLE_STUDENT
from services.permissions import HasUserRole
from django.db.models import Count, F
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import (
    Intake,
    StudentApplication,
    ApplicationDocument,
    ApplicationEducationHistory,
)
from django.contrib.auth.models import AnonymousUser
from .serializers import (
    IntakeCreateSerializer,
    IntakeListDetailSerializer,
    StudentApplicationCreateSerializer,
    StudentApplicationListDetailSerializer,
    ApplicationDocumentCreateSerializer,
    ApplicationDocumentListDetailSerializer,
    ApplicationEducationHistoryCreateSerializer,
    ApplicationEducationHistoryListDetailSerializer,
    StudentEnrollmentSerializer,
)


class IntakeCreateView(generics.CreateAPIView):
    queryset = Intake.objects.all()
    permission_classes = [IsAuthenticated]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = IntakeCreateSerializer

    def perform_create(self, serializer):
        serializer.save()


class IntakeUpdateView(generics.UpdateAPIView):
    queryset = Intake.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = IntakeCreateSerializer
    lookup_field = "pk"

    def patch(self, request, *args, **kwargs):
        intake = self.get_object()
        print("Before update:", intake.closed)

        serializer = self.get_serializer(intake, data=request.data, partial=True)
        print(f"Updating intake {intake.id} with data: {request.data}")

        if serializer.is_valid():
            serializer.save()
            print("After update:", intake.closed)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            print("Errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IntakeListView(generics.ListAPIView):
    queryset = Intake.objects.all()
    permission_classes = [IsAuthenticated]
    allowed_roles = ALL_ROLES
    serializer_class = IntakeListDetailSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IntakeFilter

    def get_queryset(self):
        return Intake.objects.all().order_by("-start_date")

    def list(self, request, *args, **kwargs):
        try:
            intakes = self.get_queryset()
            intakes = self.filter_queryset(intakes)

            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_intakes = paginator.paginate_queryset(intakes, request)
                serializer = self.get_serializer(paginated_intakes, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(intakes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class IntakeDetailView(generics.RetrieveAPIView):
    queryset = Intake.objects.all()
    permission_classes = [IsAuthenticated]
    allowed_roles = ALL_ROLES
    serializer_class = IntakeListDetailSerializer
    lookup_field = "pk"


# ================ StudentApplication Views ================


class StudentApplicationCreateView(generics.CreateAPIView):
    queryset = StudentApplication.objects.all()
    permission_classes = [IsAuthenticated]
    allowed_roles = ALL_ROLES
    serializer_class = StudentApplicationCreateSerializer

    def perform_create(self, serializer):
        serializer.save()


class StudentApplicationUpdateView(generics.UpdateAPIView):
    queryset = StudentApplication.objects.all()
    permission_classes = [IsAuthenticated]
    allowed_roles = ALL_ROLES
    serializer_class = StudentApplicationCreateSerializer
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return StudentApplication.objects.none()
        if user.role.name == ROLE_STUDENT:

            return StudentApplication.objects.filter(email=user.email)
        return StudentApplication.objects.all()

    def patch(self, request, *args, **kwargs):
        application = self.get_object()
        serializer = self.get_serializer(application, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentApplicationListView(generics.ListAPIView):
    queryset = StudentApplication.objects.all()
    permission_classes = [IsAuthenticated]
    allowed_roles = ALL_ROLES
    serializer_class = StudentApplicationListDetailSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StudentApplicationFilter
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        if user.role.name == ROLE_STUDENT:
            return StudentApplication.objects.filter(email=user.email).order_by(
                "-created_on"
            )

        applications = StudentApplication.objects.all().order_by("-created_on")
        return applications

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            filtered_queryset = self.filter_queryset(queryset)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_applications = paginator.paginate_queryset(
                    filtered_queryset, request
                )
                serializer = self.get_serializer(paginated_applications, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StudentApplicationDetailView(generics.RetrieveAPIView):
    queryset = StudentApplication.objects.all()
    serializer_class = StudentApplicationListDetailSerializer
    permission_classes = [IsAuthenticated]
    allowed_roles = ALL_ROLES
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return StudentApplication.objects.none()
        if user.role.name == ROLE_STUDENT:
            return StudentApplication.objects.filter(email=user.email)
        return StudentApplication.objects.all()


class ApplicationDocumentCreateView(generics.CreateAPIView):
    queryset = ApplicationDocument.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES
    serializer_class = ApplicationDocumentCreateSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if user.role.name == ROLE_STUDENT:
            application_id = self.request.data.get("student_application")
            try:
                application = StudentApplication.objects.get(id=application_id)
                if application.email != user.email:
                    raise ValidationError(
                        {
                            "error": "You can only upload documents to your own application."
                        }
                    )
            except StudentApplication.DoesNotExist:
                raise ValidationError({"error": "Application not found."})
        try:
            student_application = self.request.data.get("student_application")
            student_application = int(student_application)
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid application ."}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()


class ApplicationDocumentUpdateView(generics.UpdateAPIView):
    queryset = ApplicationDocument.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES
    serializer_class = ApplicationDocumentCreateSerializer
    lookup_field = "pk"

    # def get_queryset(self):
    #     user = self.request.user
    #     if isinstance(user, AnonymousUser):
    #         return ApplicationDocument.objects.none()
    #     if user.role.name == ROLE_STUDENT:

    #         return ApplicationDocument.objects.filter(
    #             student_application__email=user.email
    #         )
    #     return ApplicationDocument.objects.all()

    def patch(self, request, *args, **kwargs):
        document = self.get_object()

        if "verified" in request.data and request.user.role.name not in ALL_STAFF_ROLES:
            return Response(
                {"error": "Only staff can verify documents"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(document, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApplicationDocumentListView(generics.ListAPIView):
    queryset = ApplicationDocument.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES
    serializer_class = ApplicationDocumentListDetailSerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if user.role.name == ROLE_STUDENT:
            return ApplicationDocument.objects.filter(
                student_application__email=user.email
            ).order_by("-created_at")

        application_id = self.request.query_params.get("application_id", None)
        if application_id:
            return ApplicationDocument.objects.filter(
                student_application_id=application_id
            ).order_by("-created_at")
        return (
            ApplicationDocument.objects.all()
            .select_related("student_application")
            .order_by("-created_at")
        )


class ApplicationDocumentDetailView(generics.RetrieveDestroyAPIView):
    queryset = ApplicationDocument.objects.all()
    serializer_class = ApplicationDocumentListDetailSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return ApplicationDocument.objects.none()
        if user.role.name == ROLE_STUDENT:
            return ApplicationDocument.objects.filter(
                student_application__email=user.email
            )
        return ApplicationDocument.objects.all()


# ================ ApplicationEducationHistory Views ================


class ApplicationEducationHistoryCreateView(generics.CreateAPIView):
    queryset = ApplicationEducationHistory.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES
    serializer_class = ApplicationEducationHistoryCreateSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if user.role.name == ROLE_STUDENT:
            application_id = self.request.data.get("student_application")
            try:
                application = StudentApplication.objects.get(id=application_id)
                if application.email != user.email:
                    raise ValidationError(
                        {
                            "error": "You can only add education history to your own application."
                        }
                    )
            except StudentApplication.DoesNotExist:
                raise ValidationError({"error": "Application not found."})

        serializer.save()


class ApplicationEducationHistoryUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ApplicationEducationHistory.objects.all()
    serializer_class = ApplicationEducationHistoryCreateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return ApplicationEducationHistory.objects.none()
        if user.role.name == ROLE_STUDENT:
            return ApplicationEducationHistory.objects.filter(
                student_application__email=user.email
            )
        return ApplicationEducationHistory.objects.all()

    def patch(self, request, *args, **kwargs):
        print("request=========", request.data)
        education_history = self.get_object()
        serializer = self.get_serializer(
            education_history, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApplicationEducationHistoryListView(generics.ListAPIView):
    queryset = ApplicationEducationHistory.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES
    serializer_class = ApplicationEducationHistoryListDetailSerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if user.role.name == ROLE_STUDENT:
            return ApplicationEducationHistory.objects.filter(
                student_application__email=user.email
            ).order_by("-created_at")

        application_id = self.request.query_params.get("application_id", None)
        if application_id:
            return ApplicationEducationHistory.objects.filter(
                student_application_id=application_id
            ).order_by("-created_at")

        return (
            ApplicationEducationHistory.objects.all()
            .select_related("student_application")
            .order_by("-created_at")
        )


class ApplicationEducationHistoryDetailView(generics.RetrieveAPIView):
    queryset = ApplicationEducationHistory.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES
    serializer_class = ApplicationEducationHistoryListDetailSerializer
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return ApplicationEducationHistory.objects.none()
        if user.role.name == ROLE_STUDENT:
            return ApplicationEducationHistory.objects.filter(
                student_application__email=user.email
            )
        return ApplicationEducationHistory.objects.all()


class StudentEnrollmentView(generics.CreateAPIView):
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = StudentEnrollmentSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        application_id = data.get("application")
        cohort_id = data.get("cohort")
        campus_id = data.get("campus")

        try:
            application = StudentApplication.objects.get(id=application_id)
            documents = ApplicationDocument.objects.filter(
                student_application=application
            )
            education_history = ApplicationEducationHistory.objects.filter(
                student_application=application
            )

            try:
                role = UserRole.objects.get(name="Student")
            except UserRole.DoesNotExist:
                raise CustomAPIException(
                    message="UserRole 'Student' not found.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            try:
                cohort = ProgrammeCohort.objects.get(id=cohort_id)
            except ProgrammeCohort.DoesNotExist:
                raise CustomAPIException(
                    message="ProgrammeCohort not found.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            try:
                campus = Campus.objects.get(id=campus_id)
            except Campus.DoesNotExist:
                raise CustomAPIException(
                    message="Campus not found.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # registration_number = application.application_number
            programme = application.first_choice_programme
            level = getattr(programme, "level", "Bachelor")
            year = (
                cohort.intake.start_date.year
                if cohort.intake and cohort.intake.start_date
                else datetime.now().year
            )
            registration_number = generate_registration_number(programme, level, year)

            try:
                with transaction.atomic():
                    user = User.objects.create(
                        username=registration_number,
                        first_name=application.first_name,
                        last_name=application.last_name,
                        email=application.email,
                        phone_number=application.phone_number,
                        id_number=application.id_number,
                        passport_number=application.passport_number,
                        gender=application.gender,
                        date_of_birth=application.date_of_birth,
                        address=application.address,
                        postal_code=application.postal_code,
                        city=application.city,
                        country=application.country,
                        is_verified=True,
                        role=role,
                    )

                    user.set_password(registration_number)
                    user.save()

                    student = Student.objects.create(
                        user=user,
                        registration_number=registration_number,
                        guardian_name=application.guardian_name,
                        guardian_email=application.guardian_email,
                        guardian_phone_number=application.guardian_phone_number,
                        guardian_relationship=application.guardian_relationship,
                        programme=application.first_choice_programme,
                        status="Active",
                        cohort=cohort,
                        campus=campus if campus else None,
                    )

                    for document in documents:
                        StudentDocument.objects.create(
                            student=student,
                            document_name=document.document_name,
                            document_type=document.document_type,
                            document_file=document.document_file,
                        )

                    for history in education_history:
                        StudentEducationHistory.objects.create(
                            student=student,
                            institution=history.institution,
                            level=history.level,
                            major=history.major,
                            year=history.year,
                            grade_or_gpa=history.grade_or_gpa,
                        )

                    if application.lead:
                        application.lead.status = "Converted"
                        application.lead.save()

                    application.status = "Enrolled"
                    application.save()

                student_data = StudentListSerializer(student).data

                return Response(
                    {
                        "message": "Student enrolled successfully",
                        "student": student_data,
                    },
                    status=status.HTTP_201_CREATED,
                )

            except Exception as e:
                raise CustomAPIException(
                    message=f"Error creating user or enrolling student: {str(e)}",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        except StudentApplication.DoesNotExist:
            raise CustomAPIException(
                message="Student application not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        except CustomAPIException as exc:
            raise
        except Exception as e:
            raise CustomAPIException(
                message=f"Error enrolling student: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )


class EnrollmentsByIntakeView(generics.ListAPIView):
    """
    Returns number of enrolled applications grouped by intake,
    with optional filters for intake ID, start_date, end_date.
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EnrollmentsByIntakeFilter
    pagination_class = None

    def get_queryset(self):
        return (
            StudentApplication.objects.filter(status="Enrolled")
            .annotate(
                intake_name=F("intake__name"),
                intake_start_date=F("intake__start_date"),
            )
            .values("intake_id", "intake_name", "intake_start_date")
            .annotate(total=Count("id"))
            .order_by("intake_start_date")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return Response(queryset)
