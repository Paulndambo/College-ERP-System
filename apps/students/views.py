from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from rest_framework.exceptions import ValidationError
from django.views.generic import ListView
from django.http import JsonResponse
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from apps.users.models import User, UserRole
from apps.users.serializers import UserSerializer
from services.constants import ALL_ROLES, ALL_STAFF_ROLES, ROLE_STUDENT
from services.permissions import HasUserRole
from .models import Student, StudentProgramme
from apps.core.base_api_error_exceptions.base_exceptions import CustomAPIException
from .serializers import MealCardCreateSerializer, MealCardListSerializer, StudentCreateSerializer, StudentDocumentCreateSerializer, StudentDocumentListSerializer, StudentEducationHistoryCreateSerializer, StudentEducationHistoryListSerializer, StudentProgrammeCreateSerializer, StudentProgrammeListSerializer

from apps.students.models import (
    Student,
    StudentDocument,
    MealCard,
    StudentEducationHistory,
)
from apps.users.models import User
from apps.core.models import UserRole
from apps.schools.models import Programme, ProgrammeCohort

class StudentRegistrationView(generics.CreateAPIView):
    queryset = Student.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = StudentCreateSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        username = data.get("username")
        password = data.get("password")
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
        is_verified = True if request.user.role.name in ALL_STAFF_ROLES else data.get("is_verified", False)

     
        try:
            role = UserRole.objects.get(name="Student")
        except UserRole.DoesNotExist:
            raise CustomAPIException(
                message="UserRole 'Student' not found.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

     
        user_serializer = UserSerializer(data={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "username": username,
            "password": password,
            "gender": gender,
            "phone_number": phone_number,
            "id_number": id_number,
            "passport_number": passport_number,
            "address": address,
            "postal_code": postal_code,
            "city": city,
            "state": state,
            "country": country,
            "date_of_birth": date_of_birth,
            "is_verified": is_verified,
            "role": role.id  
        })

        if user_serializer.is_valid():
            user = user_serializer.save()
        else:
            raise ValidationError(user_serializer.errors)

        
        student_serializer = self.get_serializer(data={**data, "user": user.id})
        student_serializer.is_valid(raise_exception=True)
        self.perform_create(student_serializer)
        return Response(student_serializer.data, status=status.HTTP_201_CREATED)

class StudentUpdateView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentCreateSerializer
    lookup_field = 'pk'
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
            return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class StudentEducationHistoryListView(generics.ListAPIView):
    serializer_class = StudentEducationHistoryListSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES

    def get_queryset(self):
        user = self.request.user
        if user.role.name == ROLE_STUDENT:
            return StudentEducationHistory.objects.filter(student__user=user)
        return StudentEducationHistory.objects.all()

class StudentEducationHistoryCreateView(generics.CreateAPIView):
    serializer_class = StudentEducationHistoryCreateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES

    def perform_create(self, serializer):
        user = self.request.user
        if user.role.name == ROLE_STUDENT:
            student = Student.objects.get(user=user)
        else:
            student_id = self.request.data.get("student")
            if not student_id:
                raise ValidationError({"error": "Student  is required for staff users."})
            student = Student.objects.get(id=student_id)
        serializer.save(student=student)

class StudentEducationHistoryUpdateView(generics.UpdateAPIView):
    serializer_class = StudentEducationHistoryCreateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        if user.role.name == ROLE_STUDENT:
            student = Student.objects.get(user=user)
            return StudentEducationHistory.objects.filter(student=student)
        return StudentEducationHistory.objects.all()

    
class StudentDocumentHistoryListView(generics.ListAPIView):
    serializer_class = StudentDocumentListSerializer
    permission_classes = [HasUserRole]
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
                raise ValidationError({"student": "Student  is required for staff users."})
            student = Student.objects.get(id=student_id)
        serializer.save(student=student)
class StudentDocumentUpdateView(generics.UpdateAPIView):
    serializer_class = StudentDocumentCreateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
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
                raise ValidationError({"student": "Student  is required for staff users."})
            student = Student.objects.get(id=student_id)
        serializer.save(student=student)
        
class StudentMealCardUpdateView(generics.UpdateAPIView):
    serializer_class = MealCardCreateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
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
                raise ValidationError({"student": "Student  is required for staff users."})
            student = Student.objects.get(id=student_id)
        serializer.save(student=student)
class StudentProgrammeUpdateView(generics.UpdateAPIView):
    serializer_class = StudentProgrammeCreateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        if user.role.name == ROLE_STUDENT:
            student = Student.objects.get(user=user)
            return StudentProgramme.objects.filter(student=student)
        return StudentProgramme.objects.all()
