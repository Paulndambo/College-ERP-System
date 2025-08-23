from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics

from apps.studentsportal.courses.serializers import CourseSerializer, StudentCourseEnrollmentSerializer
from apps.schools.models import Course
from apps.students.models import Student, StudentCourseEnrollment

class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        student = Student.objects.get(user=user)
        return Course.objects.filter(programme=student.programme)
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class StudentCourseEnrollmentView(generics.ListAPIView):
    serializer_class = StudentCourseEnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        student = Student.objects.get(user=user)
        return StudentCourseEnrollment.objects.filter(student=student)
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)