from django.shortcuts import render


from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics


from apps.students.models import (
    Student,
    StudentAttendance,
    StudentDocument,
    MealCard,
    SemesterReporting,
)
from apps.studentsportal.students.serializers import (
    MealCardSerializer,
    StudentAttendanceSerializer,
    SemesterReportingSerializer,
    ExamDataSerializer,
)
from apps.exams.models import ExamData


# Create your views here.
class MealCardAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MealCardSerializer

    def get_queryset(self):
        student = Student.objects.get(user=self.request.user)
        return MealCard.objects.filter(student=student)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentAttendanceAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentAttendanceSerializer

    def get_queryset(self):
        student = Student.objects.get(user=self.request.user)
        return StudentAttendance.objects.filter(student=student)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SemesterReportingAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SemesterReportingSerializer

    def get_queryset(self):
        student = Student.objects.get(user=self.request.user)
        return SemesterReporting.objects.filter(student=student)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExamDataAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ExamDataSerializer

    def get_queryset(self):
        student = Student.objects.get(user=self.request.user)
        return ExamData.objects.filter(student=student)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
