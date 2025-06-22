from apps.finance.models import Budget
from .filters import CourseFilter, CourseSessionFilter, DepartmentFilter, ProgrammeFilter, SchoolFilter, SemesterFilter
from apps.schools.filters import CohortsFilter
from rest_framework import generics, status
from rest_framework.response import Response
from apps.core.base_api_error_exceptions.base_exceptions import CustomAPIException
from .models import School, Department, Programme, Course, Semester, ProgrammeCohort, CourseSession
from .serializers import (
    SchoolCreateSerializer, SchoolListSerializer,
    DepartmentCreateSerializer, DepartmentListSerializer,
    ProgrammeCreateSerializer, ProgrammeListSerializer,
    CourseCreateSerializer, CourseListSerializer,
    SemesterCreateSerializer, SemesterListSerializer,
    ProgrammeCohortCreateSerializer, ProgrammeCohortListSerializer,
    CourseSessionCreateSerializer, CourseSessionListSerializer
)
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
class SchoolCreateView(generics.CreateAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolCreateSerializer

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SchoolListView(generics.ListAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SchoolFilter
    pagination_class = None 
    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)
    def list(self, request, *args, **kwargs):
        try:
            schools = self.get_queryset()
            schools = self.filter_queryset(schools)
           
            
            page = request.query_params.get('page', None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_schools = paginator.paginate_queryset(schools, request)
                serializer = self.get_serializer(paginated_schools, many=True)
                return paginator.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(schools, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SchoolUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolCreateSerializer
    lookup_field = 'pk'
    http_method_names = ['patch', 'delete']

    def patch(self, request, *args, **kwargs):
        try:
           with transaction.atomic():
                school = self.get_object()

                Budget.objects.filter(school=school).update(school=None)

        
                school.delete()

                
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DepartmentCreateView(generics.CreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentCreateSerializer

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DepartmentListView(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentListSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = DepartmentFilter
    pagination_class = None 
    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)
    def get(self, request, *args, **kwargs):
        try:
            departments = self.get_queryset()
            departments = self.filter_queryset(departments)
            page = request.query_params.get('page', None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_departments = paginator.paginate_queryset(departments, request)
                serializer = self.get_serializer(paginated_departments, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(departments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DepartmentUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentCreateSerializer
    lookup_field = 'pk'
    http_method_names = ['patch', 'delete']

    def patch(self, request, *args, **kwargs):
        try:
            return super().patch(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProgrammeCreateView(generics.CreateAPIView):
    queryset = Programme.objects.all()
    serializer_class = ProgrammeCreateSerializer

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProgrammeListView(generics.ListAPIView):
    queryset = Programme.objects.all()
    serializer_class = ProgrammeListSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProgrammeFilter
    pagination_class = None 
    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)
    def list(self, request, *args, **kwargs):
        try:
            programmes = self.get_queryset()
            programmes = self.filter_queryset(programmes)
            page = request.query_params.get('page', None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_programmes = paginator.paginate_queryset(programmes, request)
                serializer = self.get_serializer(paginated_programmes, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(programmes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProgrammeUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Programme.objects.all()
    serializer_class = ProgrammeCreateSerializer
    lookup_field = 'pk'
    http_method_names = ['patch', 'delete']

    def patch(self, request, *args, **kwargs):
        try:
            return super().patch(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CourseCreateView(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseCreateSerializer

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseListSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = CourseFilter
    def get(self, request, *args, **kwargs):
        try:
            courses = self.get_queryset()
            courses = self.filter_queryset(courses)
            page = self.paginate_queryset(courses)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CourseUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseCreateSerializer
    lookup_field = 'pk'
    http_method_names = ['patch', 'delete']

    def patch(self, request, *args, **kwargs):
        try:
            return super().patch(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SemesterCreateView(generics.CreateAPIView):
    queryset = Semester.objects.all()
    serializer_class = SemesterCreateSerializer

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SemesterListView(generics.ListAPIView):
    queryset = Semester.objects.all()
    serializer_class = SemesterListSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = SemesterFilter
    pagination_class = None 
    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)
    def get(self, request, *args, **kwargs):
        try:
            semesters = self.get_queryset()
            semesters = self.filter_queryset(semesters)
            page = request.query_params.get('page', None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_semesters = paginator.paginate_queryset(semesters, request)
                serializer = self.get_serializer(paginated_semesters, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(semesters, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SemesterUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Semester.objects.all()
    serializer_class = SemesterCreateSerializer
    lookup_field = 'pk'
    http_method_names = ['patch', 'delete']

    def patch(self, request, *args, **kwargs):
        try:
            return super().patch(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProgrammeCohortCreateView(generics.CreateAPIView):
    queryset = ProgrammeCohort.objects.all()
    serializer_class = ProgrammeCohortCreateSerializer

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProgrammeCohortListView(generics.ListAPIView):
    queryset = ProgrammeCohort.objects.all()
    serializer_class = ProgrammeCohortListSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = CohortsFilter
    pagination_class = None 
    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)
    def get(self, request, *args, **kwargs):
        try:
            cohorts = self.get_queryset()
            cohorts = self.filter_queryset(cohorts)
            page = request.query_params.get('page', None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_schools = paginator.paginate_queryset(cohorts, request)
                serializer = self.get_serializer(paginated_schools, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(cohorts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProgrammeCohortUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProgrammeCohort.objects.all()
    serializer_class = ProgrammeCohortCreateSerializer
    lookup_field = 'pk'
    http_method_names = ['patch', 'delete']

    def patch(self, request, *args, **kwargs):
        try:
            return super().patch(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CourseSessionCreateView(generics.CreateAPIView):
    queryset = CourseSession.objects.all()
    serializer_class = CourseSessionCreateSerializer

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CourseSessionListView(generics.ListAPIView):
    queryset = CourseSession.objects.all()
    serializer_class = CourseSessionListSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = CourseSessionFilter
    def get(self, request, *args, **kwargs):
        try:
            sessions = self.get_queryset()
            sessions = self.filter_queryset(sessions)
            page = self.paginate_queryset(sessions)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(sessions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CourseSessionUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CourseSession.objects.all()
    serializer_class = CourseSessionCreateSerializer
    lookup_field = 'pk'
    http_method_names = ['patch', 'delete']

    def patch(self, request, *args, **kwargs):
        try:
            return super().patch(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
