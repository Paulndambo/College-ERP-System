from apps.core.base_api_error_exceptions.base_exceptions import CustomAPIException
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Count
from rest_framework.views import APIView
from .filters import AssessmentFilter, StudentFilter
from rest_framework.exceptions import ValidationError
from django.views.generic import ListView
from django.http import JsonResponse
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
import pandas as pd
from rest_framework.views import APIView
import io
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from apps.users.models import User, UserRole
from apps.users.serializers import AdminUserSerializer, UserSerializer
from services.constants import ALL_ROLES, ALL_STAFF_ROLES, ROLE_STUDENT
from services.permissions import HasUserRole
from .models import SemesterReporting, Student, StudentProgramme
from django.contrib.auth.models import AnonymousUser
from .serializers import (
    MealCardCreateSerializer,
    MealCardListSerializer,
    StudentCreateSerializer,
    StudentDetailSerialzer,
    StudentDocumentCreateSerializer,
    StudentDocumentListSerializer,
    StudentEducationHistoryCreateSerializer,
    StudentEducationHistoryListSerializer,
    StudentListSerializer,
    StudentProgrammeCreateSerializer,
    StudentProgrammeListSerializer,
)
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from apps.students.models import (
    Student,
    StudentDocument,
    MealCard,
    StudentEducationHistory,
)
from apps.users.models import User
from apps.core.models import UserRole
from apps.schools.models import Programme, ProgrammeCohort, Semester
from django.db import transaction


class StudentRegistrationView(generics.CreateAPIView):
    queryset = Student.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = StudentCreateSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data

        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        gender = data.get("gender")
        phone_number = data.get("phone_number")
        id_number = data.get("id_number")
        passport_number = data.get("passport_number")
        address = data.get("address")
        postal_code = data.get("postal_code")
        city = data.get("city")
        state = data.get("state")
        country = data.get("country")
        date_of_birth = data.get("date_of_birth")
        role_id = data.get("role")
        registration_number = data.get("registration_number")

        # Check duplicate registration_number on Student
        if Student.objects.filter(registration_number=registration_number).exists():
            return Response(
                {
                    "success": False,
                    "error": f"Student with registration number '{registration_number}' already exists",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Role check
        try:
            role = UserRole.objects.get(id=role_id)
        except UserRole.DoesNotExist:
            return Response(
                {"success": False, "error": "Role not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Duplicate username/email on User
        if User.objects.filter(username=registration_number).exists():
            return Response(
                {
                    "success": False,
                    "error": f"User with username '{registration_number}' already exists",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if email and User.objects.filter(email=email).exists():
            return Response(
                {
                    "success": False,
                    "error": f"User with email '{email}' already exists",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create User
        try:
            user = User.objects.create(
                username=registration_number,
                email=email,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                phone_number=phone_number,
                id_number=id_number,
                passport_number=passport_number,
                address=address,
                postal_code=postal_code,
                city=city,
                state=state,
                country=country,
                date_of_birth=date_of_birth,
                role=role,
            )
            user.set_password(registration_number)
            user.save()
        except Exception as e:
            return Response(
                {"success": False, "error": f"Error creating user: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create Student linked to the user
        student_serializer = self.get_serializer(
            data={**data, "user": user.id, "status": "Active"}
        )
        student_serializer.is_valid(raise_exception=True)
        self.perform_create(student_serializer)

        return Response(student_serializer.data, status=status.HTTP_201_CREATED)


class StudentUpdateView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentCreateSerializer
    lookup_field = "pk"
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES

    def get_object(self):
        student = super().get_object()
        return super().get_object()

    def patch(self, request, *args, **kwargs):
        student = self.get_object()
        data = request.data

        student_serializer = self.get_serializer(student, data=data, partial=True)

        if student_serializer.is_valid():
            student_serializer.save()
            return Response(student_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                student_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


class StudentAccountUpdateView(generics.UpdateAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    lookup_field = "pk"

    def get_queryset(self):
        return User.objects.filter(role__name="Student")


class StudentListView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentListSerializer
    permission_classes = [IsAuthenticated]
    allowed_roles = ALL_STAFF_ROLES
    filter_backends = [DjangoFilterBackend]
    filterset_class = StudentFilter
    pagination_class = None

    def get_queryset(self):
        return (
            Student.objects.all()
            .select_related("user", "programme", "cohort", "campus")
            .order_by("-created_on")
        )

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            students = self.get_queryset()
            students = self.filter_queryset(students)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_students = paginator.paginate_queryset(students, request)
                serializer = self.get_serializer(paginated_students, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(students, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AssessmentList(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentDetailSerialzer
    permission_classes = [IsAuthenticated]
    allowed_roles = ALL_STAFF_ROLES
    filter_backends = [DjangoFilterBackend]
    filterset_class = AssessmentFilter
    pagination_class = None

    def get_queryset(self):
        return (
            Student.objects.all()
            .select_related("user", "programme", "cohort", "campus")
            .order_by("-created_on")
        )

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):

        course = self.request.query_params.get("course", None)
        semester = self.request.query_params.get("semester", None)
        cohort = self.request.query_params.get("cohort", None)

        try:
            students = self.get_queryset()
            students = self.filter_queryset(students)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_students = paginator.paginate_queryset(students, request)
                serializer = self.get_serializer(paginated_students, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(students, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StudentDetailView(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentDetailSerialzer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    look_up_field = "pk"


class StudentEducationHistoryListView(generics.ListAPIView):
    serializer_class = StudentEducationHistoryListSerializer
    permission_classes = [IsAuthenticated]
    allowed_roles = ALL_ROLES

    def get_queryset(self):
        user = self.request.user
        if user.role.name == ROLE_STUDENT:
            return StudentEducationHistory.objects.filter(student__user=user)
        return StudentEducationHistory.objects.all()


class StudentEducationHistoryCreateView(generics.CreateAPIView):
    serializer_class = StudentEducationHistoryCreateSerializer
    permission_classes = [IsAuthenticated]
    allowed_roles = ALL_ROLES

    def perform_create(self, serializer):
        user = self.request.user
        if user.role.name == ROLE_STUDENT:
            student = Student.objects.get(user=user)
        else:
            student_id = self.request.data.get("student")
            if not student_id:
                raise ValidationError(
                    {"error": "Student  is required for staff users."}
                )
            student = Student.objects.get(id=student_id)
        serializer.save(student=student)


class StudentEducationHistoryUpdateView(generics.UpdateAPIView):
    serializer_class = StudentEducationHistoryCreateSerializer
    permission_classes = [IsAuthenticated]
    allowed_roles = ALL_ROLES
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return StudentEducationHistory.objects.none()
        if user.role.name == ROLE_STUDENT:
            student = Student.objects.get(user=user)
            return StudentEducationHistory.objects.filter(student=student)
        return StudentEducationHistory.objects.all()


class StudentDocumentHistoryListView(generics.ListAPIView):
    serializer_class = StudentDocumentListSerializer
    permission_classes = [IsAuthenticated]
    allowed_roles = ALL_ROLES

    def get_queryset(self):
        user = self.request.user
        if user.role.name == ROLE_STUDENT:
            return StudentDocument.objects.filter(student__user=user)
        return StudentDocument.objects.all()


class StudentDocumentCreateView(generics.CreateAPIView):
    serializer_class = StudentDocumentCreateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES

    def perform_create(self, serializer):
        user = self.request.user
        if user.role.name == ROLE_STUDENT:
            student = Student.objects.get(user=user)
        else:
            student_id = self.request.data.get("student")
            if not student_id:
                raise ValidationError(
                    {"student": "Student  is required for staff users."}
                )
            student = Student.objects.get(id=student_id)
        serializer.save(student=student)


class StudentDocumentUpdateView(generics.UpdateAPIView):
    serializer_class = StudentDocumentCreateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return StudentDocument.objects.none()
        if user.role.name == ROLE_STUDENT:
            student = Student.objects.get(user=user)
            return StudentDocument.objects.filter(student=student)
        return StudentDocument.objects.all()


class StudentMealCardListView(generics.ListAPIView):
    serializer_class = MealCardListSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES

    def get_queryset(self):
        user = self.request.user
        if user.role.name == ROLE_STUDENT:
            return MealCard.objects.filter(student__user=user)
        return MealCard.objects.all()


class StudentMealCardCreateView(generics.CreateAPIView):
    serializer_class = MealCardCreateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES

    def perform_create(self, serializer):
        user = self.request.user
        if user.role.name == ROLE_STUDENT:
            student = Student.objects.get(user=user)
        else:
            student_id = self.request.data.get("student")
            if not student_id:
                raise ValidationError(
                    {"student": "Student  is required for staff users."}
                )
            student = Student.objects.get(id=student_id)
        serializer.save(student=student)


class StudentMealCardUpdateView(generics.UpdateAPIView):
    serializer_class = MealCardCreateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return MealCard.objects.none()
        if user.role.name == ROLE_STUDENT:
            student = Student.objects.get(user=user)
            return MealCard.objects.filter(student=student)
        return MealCard.objects.all()


class StudentProgrameListView(generics.ListAPIView):
    serializer_class = StudentProgrammeListSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES

    def get_queryset(self):
        user = self.request.user
        if user.role.name == ROLE_STUDENT:
            return StudentProgramme.objects.filter(student__user=user)
        return StudentProgramme.objects.all()


class StudentProgrameCreateView(generics.CreateAPIView):
    serializer_class = StudentProgrammeCreateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES

    def perform_create(self, serializer):
        user = self.request.user
        if user.role.name == ROLE_STUDENT:
            student = Student.objects.get(user=user)
        else:
            student_id = self.request.data.get("student")
            if not student_id:
                raise ValidationError(
                    {"student": "Student  is required for staff users."}
                )
            student = Student.objects.get(id=student_id)
        serializer.save(student=student)


class StudentProgrammeUpdateView(generics.UpdateAPIView):
    serializer_class = StudentProgrammeCreateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return StudentProgramme.objects.none()
        if user.role.name == ROLE_STUDENT:
            student = Student.objects.get(user=user)
            return StudentProgramme.objects.filter(student=student)
        return StudentProgramme.objects.all()


class BulkStudentUploadView(generics.CreateAPIView):
    """
    API endpoint for staff members to upload multiple students via CSV or Excel file.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = StudentCreateSerializer

    def post(self, request, *args, **kwargs):
        if "file" not in request.FILES:
            return Response(
                {"error": "No file was uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )
        programme = request.data.get("programme")
        cohort = request.data.get("cohort")
        campus = request.data.get("campus")
        role_id = request.data.get("role")
        # print("programme", programme)
        try:
            programme = int(programme)
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid programme ID."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            cohort = int(cohort)
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid cohort ID."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            campus = int(campus)
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid campus ID."}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["file"]

        file_extension = file.name.split(".")[-1].lower()
        if file_extension not in ["csv", "xls", "xlsx"]:
            raise CustomAPIException(
                "No file was uploaded.", status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            if file_extension == "csv":
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            raise CustomAPIException(
                f"Error reading file: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST
            )

        required_columns = [
            "first_name",
            "last_name",
            "email",
            "gender",
            "phone_number",
            "address",
            "city",
            "date_of_birth",
            "registration_number",
        ]

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return Response(
                {"error": f"Missing required columns: {', '.join(missing_columns)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_count = 0
        errors = []

        try:

            try:
                student_role = UserRole.objects.get(id=role_id)
                print("student_role===========", student_role)
            except UserRole.DoesNotExist:
                return Response(
                    {"success": False, "error": f"Role not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            for index, row in df.iterrows():
                try:

                    with transaction.atomic():
                        student_data = {
                            "first_name": str(row["first_name"]).strip(),
                            "last_name": str(row["last_name"]).strip(),
                            "email": str(row["email"]).strip(),
                            "gender": str(row["gender"]).strip(),
                            "phone_number": str(row["phone_number"]).strip(),
                            "address": str(row["address"]).strip(),
                            "city": str(row["city"]).strip(),
                            "date_of_birth": pd.to_datetime(
                                row["date_of_birth"]
                            ).strftime("%Y-%m-%d"),
                            "registration_number": str(
                                row["registration_number"]
                            ).strip(),
                            "is_verified": True,
                        }

                        optional_fields = {
                            "id_number": "id_number",
                            "passport_number": "passport_number",
                            "postal_code": "postal_code",
                            "state": "state",
                            "country": "country",
                        }

                        for model_field, df_field in optional_fields.items():
                            if df_field in df.columns and pd.notna(row[df_field]):
                                student_data[model_field] = str(row[df_field]).strip()

                        # Create the user object
                        user = User.objects.create(
                            username=student_data["registration_number"],
                            email=student_data["email"],
                            first_name=student_data["first_name"],
                            last_name=student_data["last_name"],
                            gender=student_data["gender"],
                            phone_number=student_data["phone_number"],
                            address=student_data["address"],
                            city=student_data["city"],
                            date_of_birth=student_data["date_of_birth"],
                            is_verified=student_data["is_verified"],
                            role=student_role,
                            id_number=student_data.get("id_number"),
                            passport_number=student_data.get("passport_number"),
                            postal_code=student_data.get("postal_code"),
                            state=student_data.get("state"),
                            country=student_data.get("country"),
                        )

                        user.set_password(student_data["registration_number"])
                        user.save()

                        student_serializer = StudentCreateSerializer(
                            data={
                                **student_data,
                                "user": user.id,
                                "status": "Active",
                                "programme": programme,
                                "cohort": cohort,
                                "campus": campus,
                            }
                        )

                        if student_serializer.is_valid():
                            student_serializer.save()
                            created_count += 1
                        else:
                            user.delete()
                            errors.append(
                                {
                                    "row": index + 2,
                                    "registration_number": student_data[
                                        "registration_number"
                                    ],
                                    "errors": student_serializer.errors,
                                }
                            )

                except Exception as e:
                    errors.append(
                        {
                            "row": index + 2,
                            "registration_number": row.get(
                                "registration_number", f"Row {index + 2}"
                            ),
                            "error": str(e),
                        }
                    )

        except Exception as e:
            raise CustomAPIException(
                {f"Error processing file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if created_count == 0:
            raise CustomAPIException(
                "Students Upload failed.Look for duplicate entries or missing required fields.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "success": True,
                "count": created_count,
                "failed_count": len(errors),
                "errors": errors if errors else None,
            },
            status=status.HTTP_201_CREATED,
        )


class StudentMetricsView(APIView):
    """
    Returns counts of students by status.
    Applies optional filters: campus, cohort, programme, status, semester.
    """

    def get(self, request, *args, **kwargs):
        # All students
        qs = Student.objects.all()

        # Apply filters
        filtered_qs = StudentFilter(request.GET, queryset=qs).qs

        # Count by status
        counts = filtered_qs.values("status").annotate(count=Count("id"))

        # Build dictionary with all statuses from the model
        status_labels = [
            choice[0] for choice in Student._meta.get_field("status").choices
        ]
        metrics = {status: 0 for status in status_labels}

        for item in counts:
            metrics[item["status"]] = item["count"]

        metrics["total_students"] = filtered_qs.count()

        return Response(metrics)
