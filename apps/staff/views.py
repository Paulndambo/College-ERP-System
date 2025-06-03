from apps.core.base_api_error_exceptions.base_exceptions import CustomAPIException
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages

from apps.staff.models import Staff
from apps.staff.serializers import StaffCreateSerializer, StaffListDetailSerializer
from .filters import StaffFilter
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
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from apps.users.models import User, UserRole
from apps.users.serializers import AdminUserSerializer, UserSerializer
from services.constants import ALL_ROLES, ALL_STAFF_ROLES, ROLE_STUDENT
from services.permissions import HasUserRole

from django.contrib.auth.models import AnonymousUser

from rest_framework.pagination import PageNumberPagination
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
        is_verified = (
            True
            if request.user.role.name in ALL_STAFF_ROLES
            else data.get("is_verified", False)
        )
        staff_number = data.get("staff_number")

        try:
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
                role=role,
            )

            user.set_password(staff_number)
            user.save()
        except Exception as e:
            raise CustomAPIException(
                message=f"Error creating user: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        staff_serializer = self.get_serializer(
            data={**data, "user": user.id, "status": "Active"}
        )
        staff_serializer.is_valid(raise_exception=True)
        self.perform_create(staff_serializer)
        return Response(staff_serializer.data, status=status.HTTP_201_CREATED)


class StaffUpdateView(generics.UpdateAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffCreateSerializer
    lookup_field = "pk"
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES

    def get_object(self):
        staff = super().get_object()
        return super().get_object()

    def patch(self, request, *args, **kwargs):
        staff = self.get_object()
        data = request.data

        staff_serializer = self.get_serializer(staff, data=data, partial=True)

        if staff_serializer.is_valid():
            staff_serializer.save()
            return Response(staff_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(staff_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffAccountUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    lookup_field = "pk"

    

class StaffUpdateView(generics.UpdateAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffCreateSerializer
    lookup_field = "pk"
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        staff = self.get_object()
        data = request.data

        
        if staff.user:
            user = staff.user
            user_fields = [
                "first_name",
                "last_name",
                "email",
                "gender",
                "phone_number",
                "id_number",
                "passport_number",
                "address",
                "postal_code",
                "city",
                "state",
                "country",
                "date_of_birth",
                "role",
                "is_verified",
            ]

            for field in user_fields:
                if field in data:
                    setattr(user, field, data[field])

            if "staff_number" in data:
                user.username = data["staff_number"]

            user.save()

        staff_serializer = self.get_serializer(staff, data=data, partial=True)
        staff_serializer.is_valid(raise_exception=True)
        staff_serializer.save()

        return Response(staff_serializer.data, status=status.HTTP_200_OK)


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
