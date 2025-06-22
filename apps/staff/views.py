from apps.core.base_api_error_exceptions.base_exceptions import CustomAPIException
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages

from apps.schools.models import Department
from apps.staff.models import (
    Payslip,
    Staff,
    StaffDocuments,
    StaffLeave,
    StaffLeaveApplication,
    StaffLeaveEntitlement,
    StaffOnboardingProgress,
    StaffPayroll,
    StaffPosition,
)
from rest_framework.views import APIView
from apps.staff.serializers import (
    CompleteOnboardingSerializer,
    CreateStaffLeaveApplicationSerializer,
    CreateUpdateStaffLeaveSerializer,
    StaffCreateSerializer,
    StaffDocumentCreateSerializer,
    StaffDocumentListSerializer,
    StaffDocumentMultiCreateSerializer,
    StaffLeaveApplicationListSerializer,
    StaffLeaveSerializer,
    StaffListDetailSerializer,
    StaffOnboardingProgressListSerializer,
    StaffPaySlipSerializer,
    StaffPayrollCreateSerializer,
    StaffPayrollListSerializer,
    StaffPositionListSerializer,
    StaffStatusSerializer,
)
import json
from .filters import PayrollFilter, PayslipFilter, StaffFilter, StaffLeaveApplicationFilter, StaffLeaveFilter
from rest_framework.exceptions import ValidationError
from django.views.generic import ListView
from django.http import JsonResponse
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
import pandas as pd
import io
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from apps.users.models import User, UserRole
from apps.users.serializers import AdminUserSerializer, UserSerializer
from services.constants import ALL_ROLES, ALL_STAFF_ROLES, ROLE_ADMIN, ROLE_STUDENT
from services.permissions import HasUserRole

from django.contrib.auth.models import AnonymousUser

from django_filters.rest_framework import DjangoFilterBackend


from apps.users.models import User
from apps.core.models import UserRole


class CreateStaffView(generics.CreateAPIView):
    queryset = Staff.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = StaffCreateSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        gender = data.get("gender")
        phone_number = data.get("phone_number")
        id_number = data.get("id_number", None)
        passport_number = data.get("passport_number", None)
        address = data.get("address")
        postal_code = data.get("postal_code", None)
        city = data.get("city")
        state = data.get("state", None)
        country = data.get("country", None)
        date_of_birth = data.get("date_of_birth")
        role = data.get("role")
        department_id = data.get("department")
        position = data.get("position", None)

        try:
            department = Department.objects.get(id=department_id)
            print(f"Department found: {department.name}")
        except Department.DoesNotExist:
            raise CustomAPIException(
                message="Department not found",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user_role = UserRole.objects.get(id=role)
            print(f"Role found: {user_role.name}")
        except UserRole.DoesNotExist:
            raise CustomAPIException(
                message="Role not found",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(email=email).exists():
            raise CustomAPIException(
                message="A user with this email already exists",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if id_number and User.objects.filter(id_number=id_number).exists():
            raise CustomAPIException(
                message="A user with this ID number already exists",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(phone_number=phone_number).exists():
            raise CustomAPIException(
                message="A user with this phone number already exists",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            staff_number = Staff.generate_staff_number(department)
            print("Generated staff_number:", staff_number)
        except ValueError as e:
            raise CustomAPIException(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if Staff.objects.filter(staff_number=staff_number).exists():
            raise CustomAPIException(
                message=f"Staff with staff number {staff_number} already exists",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=staff_number).exists():
            raise CustomAPIException(
                message=f"User with username {staff_number} already exists",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        print("staff_number", staff_number)
        is_verified = (
            True
            if request.user.role.name in ALL_STAFF_ROLES
            else data.get("is_verified", False)
        )

        try:
            with transaction.atomic():
                user = User.objects.create(
                    username=staff_number,
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
                    is_verified=is_verified,
                    role=user_role,
                )

                user.set_password(staff_number)
                user.save()

                staff_serializer = self.get_serializer(
                    data={**data, "user": user.id, "status": "Active"}
                )
                staff_serializer.is_valid(raise_exception=True)

                staff = staff_serializer.save(staff_number=staff_number)
                StaffOnboardingProgress.objects.create(
                    staff=staff,
                    user_created=True,
                    staff_details_completed=True,
                    payroll_setup_completed=False,
                    documents_uploaded=False,
                )
                return Response(
                    {
                        **staff_serializer.data,
                        "staff_number": staff_number,
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            raise CustomAPIException(
                message=f"Error creating staff: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )


class StaffUpdateView(generics.UpdateAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffCreateSerializer
    lookup_field = "pk"
    permission_classes = [HasUserRole]
    allowed_roles = ROLE_ADMIN


class StaffDetailAPIView(generics.RetrieveAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffListDetailSerializer
    lookup_field = "pk"
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES


class StaffStatusToggleView(APIView):
    def post(self, request, pk):
        try:
            staff = Staff.objects.get(pk=pk)
        except Staff.DoesNotExist:
            return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if staff.status == "Inactive":
            if staff.onboarding_status != "Completed":
                return Response(
                    {"error": "Cannot activate staff before onboarding is completed."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            staff.status = "Active"
        else:

            staff.status = "Inactive"

        staff.save()

        serializer = StaffStatusSerializer(staff)
        return Response(serializer.data)


class StaffListView(generics.ListAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffListDetailSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    filter_backends = [DjangoFilterBackend]
    filterset_class = StaffFilter
    pagination_class = None

    def get_queryset(self):
        return Staff.objects.all().order_by("-created_on")

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            staff = self.get_queryset()
            staff = self.filter_queryset(staff)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_staff = paginator.paginate_queryset(staff, request)
                serializer = self.get_serializer(paginated_staff, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(staff, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StaffPaySlipListView(generics.ListAPIView):
    queryset = Payslip.objects.all()
    serializer_class = StaffPaySlipSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    filter_backends = [DjangoFilterBackend]
    filterset_class = PayslipFilter
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Payslip.objects.all().order_by("-created_on")

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            queryset = self.filter_queryset(queryset)
            page = self.request.query_params.get("page", None)
            if page:

                paginator = self.pagination_class()
                paginated_queryset = paginator.paginate_queryset(queryset, request)
                serializer = self.get_serializer(paginated_queryset, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StaffPayrollCreateView(generics.CreateAPIView):
    queryset = StaffPayroll.objects.all()
    serializer_class = StaffPayrollCreateSerializer


class StaffPayrollListView(generics.ListAPIView):
    queryset = StaffPayroll.objects.all()
    serializer_class = StaffPayrollListSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    filter_backends = [DjangoFilterBackend]
    filterset_class = PayrollFilter
    pagination_class = None

    def get_queryset(self):
        return StaffPayroll.objects.all().order_by("-created_on")

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            payroll_list = self.get_queryset()
            payroll_list = self.filter_queryset(payroll_list)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_payroll_list = paginator.paginate_queryset(
                    payroll_list, request
                )
                serializer = self.get_serializer(paginated_payroll_list, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(payroll_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StaffPayrollDetailView(generics.RetrieveAPIView):
    queryset = StaffPayroll.objects.all()
    serializer_class = StaffPayrollCreateSerializer
    lookup_field = "pk"


class StaffOnboardingProgressAPIView(generics.RetrieveAPIView):
    queryset = StaffOnboardingProgress.objects.all()
    serializer_class = StaffOnboardingProgressListSerializer
    lookup_field = "pk"


class StaffDocumentCreateView(generics.CreateAPIView):
    queryset = StaffDocuments.objects.all()
    serializer_class = StaffDocumentMultiCreateSerializer

    def create(self, request, *args, **kwargs):
        documents_json = request.data.get("documents")
        print("documents_json", documents_json)
        if not documents_json:
            return Response(
                {"error": "Missing documents metadata"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            documents_data = json.loads(documents_json)
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid JSON for documents"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        files = []
        i = 0
        while True:
            file_key = f"document_files[{i}]"
            if file_key in request.FILES:
                files.append(request.FILES[file_key])
                i += 1
            else:
                break

        if len(files) != len(documents_data):
            return Response(
                {
                    "error": "Number of files and document metadata entries do not match."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        for idx, doc in enumerate(documents_data):
            doc["document_file"] = files[idx]

        data = {
            "staff": request.data.get("staff"),
            "documents": documents_data,
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        created_documents = serializer.save()

        return Response(
            {"message": "Documents uploaded successfully."},
            status=status.HTTP_201_CREATED,
        )


class StaffDocumentListView(generics.ListAPIView):
    queryset = StaffDocuments.objects.all()
    serializer_class = StaffDocumentListSerializer


class StaffPayrollUpdateView(generics.RetrieveUpdateAPIView):
    queryset = StaffPayroll.objects.all()
    serializer_class = StaffPayrollCreateSerializer
    lookup_field = "pk"


class StaffDocumentUpdateView(generics.RetrieveUpdateAPIView):
    queryset = StaffDocuments.objects.all()
    serializer_class = StaffDocumentCreateSerializer
    lookup_field = "pk"


class CompleteOnboardingView(generics.UpdateAPIView):
    queryset = StaffOnboardingProgress.objects.all()
    serializer_class = CompleteOnboardingSerializer
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.onboarding_completed:
            return Response(
                {
                    "message": "Onboarding already completed",
                    "staff": str(instance.staff),
                    "completed_on": instance.updated_on,
                },
                status=status.HTTP_200_OK,
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {
                "message": "Onboarding completed successfully",
                "staff": str(instance.staff),
                "data": serializer.data,
            }
        )


class PositionListView(generics.ListAPIView):
    queryset = StaffPosition.objects.all()
    serializer_class = StaffPositionListSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    filter_backends = [DjangoFilterBackend]

    pagination_class = None

    def get_queryset(self):
        return StaffPosition.objects.all().order_by("-created_on")

    def get_paginated_response(self, data):
        return super().get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            positions = self.get_queryset()
            positions = self.filter_queryset(positions)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_positions = paginator.paginate_queryset(positions, request)
                serializer = self.get_serializer(paginated_positions, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(positions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class StaffLeaveApplicationListView(generics.ListAPIView):
    queryset = StaffLeaveApplication.objects.all()
    serializer_class = StaffLeaveApplicationListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StaffLeaveApplicationFilter
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    pagination_class = None
    
    def get_queryset(self):
        return StaffLeaveApplication.objects.all().order_by("-created_on")

    def get_paginated_response(self, data):
        return super().get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            leave_applications = self.get_queryset()
            leave_applications = self.filter_queryset(leave_applications)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_leave_applications = paginator.paginate_queryset(leave_applications, request)
                serializer = self.get_serializer(paginated_leave_applications, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(leave_applications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class StaffLeaveApplicationCreateView(generics.CreateAPIView):
    queryset = StaffLeaveApplication.objects.all()
    serializer_class = CreateStaffLeaveApplicationSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    def perform_create(self, serializer):
        user = self.request.user

        if user.role.name == ROLE_ADMIN:
            staff = serializer.validated_data.get("staff")
            if not staff:
                raise ValidationError({"staff": "This field is required for admin users."})
        else:
            
            try:
                staff = Staff.objects.get(user=user)
            except Staff.DoesNotExist:
                raise ValidationError("Staff record not found for this user.")

        serializer.save(staff=staff)


class StaffLeaveApplicationUpdateView(generics.UpdateAPIView):
    queryset = StaffLeaveApplication.objects.all()
    serializer_class = CreateStaffLeaveApplicationSerializer
    lookup_field = 'pk'
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES

    
    def perform_update(self, serializer):
            updated_instance = serializer.save()

            if updated_instance.status == 'Approved':
                leave_days = updated_instance.leave_days_applied_for()
                print("leave days in views", leave_days)
                if updated_instance.leave_type != "Emergency":
                    entitlement = StaffLeaveEntitlement.objects.get(staff=updated_instance.staff, year=updated_instance.start_date.year)
                    entitlement.used_days += leave_days
                    entitlement.save()

                if not StaffLeave.objects.filter(application=updated_instance).exists():
                    StaffLeave.objects.create(application=updated_instance, status='Active')




class StaffLeaveListView(generics.ListAPIView):
    queryset = StaffLeave.objects.all()
    serializer_class = StaffLeaveSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StaffLeaveFilter
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    pagination_class = None
    def get_queryset(self):
        return StaffLeave.objects.all().order_by("-created_on")
    def get_paginated_response(self, data):
        return super().get_paginated_response(data)
    def list(self, request, *args, **kwargs):
        try:
            leaves = self.get_queryset()
            leaves = self.filter_queryset(leaves)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_leaves = paginator.paginate_queryset(leaves, request)
                serializer = self.get_serializer(paginated_leaves, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(leaves, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


