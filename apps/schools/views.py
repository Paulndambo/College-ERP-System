from apps.finance.models import Budget
from services.constants import ALL_ROLES, ROLE_STUDENT
from services.permissions import HasUserRole
from .filters import (
    CourseFilter,
    CourseSessionFilter,
    DepartmentFilter,
    ProgrammeFilter,
    SchoolFilter,
    SemesterFilter,
)
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from apps.schools.filters import CohortsFilter
from rest_framework import generics, status
from rest_framework.response import Response
from apps.core.base_api_error_exceptions.base_exceptions import CustomAPIException
from .models import (
    School,
    Department,
    Programme,
    Course,
    Semester,
    ProgrammeCohort,
    CourseSession,
)
from .serializers import (
    ProgrammeListDetailSerializer,
    SchoolCreateSerializer,
    SchoolListSerializer,
    DepartmentCreateSerializer,
    DepartmentListSerializer,
    ProgrammeCreateSerializer,
    ProgrammeListSerializer,
    CourseCreateSerializer,
    CourseListSerializer,
    SemesterCreateSerializer,
    SemesterListSerializer,
    ProgrammeCohortCreateSerializer,
    ProgrammeCohortListSerializer,
    CourseSessionCreateSerializer,
    CourseSessionListSerializer,
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
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SchoolListView(generics.ListAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SchoolFilter
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            schools = self.get_queryset()
            schools = self.filter_queryset(schools)

            page = request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_schools = paginator.paginate_queryset(schools, request)
                serializer = self.get_serializer(paginated_schools, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(schools, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SchoolUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolCreateSerializer
    lookup_field = "pk"
    http_method_names = ["patch", "delete"]

    def patch(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                return self.partial_update(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                school = self.get_object()
                Budget.objects.filter(school=school).update(school=None)
                school.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DepartmentListView(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentListSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = DepartmentFilter
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def get(self, request, *args, **kwargs):
        try:
            departments = self.get_queryset()
            departments = self.filter_queryset(departments)
            page = request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_departments = paginator.paginate_queryset(
                    departments, request
                )
                serializer = self.get_serializer(paginated_departments, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(departments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DepartmentUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentCreateSerializer
    lookup_field = "pk"
    http_method_names = ["patch", "delete"]

    def patch(self, request, *args, **kwargs):
        try:
            return super().patch(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProgrammeListView(generics.ListAPIView):
    queryset = Programme.objects.all()
    serializer_class = ProgrammeListSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProgrammeFilter
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            programmes = self.get_queryset()
            programmes = self.filter_queryset(programmes)
            page = request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_programmes = paginator.paginate_queryset(programmes, request)
                serializer = self.get_serializer(paginated_programmes, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(programmes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProgrammeUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Programme.objects.all()
    serializer_class = ProgrammeCreateSerializer
    lookup_field = "pk"
    http_method_names = ["patch", "delete"]

    def patch(self, request, *args, **kwargs):
        try:
            return super().patch(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProgammeDetailView(generics.RetrieveAPIView):
    queryset = Programme.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_ROLES
    serializer_class = ProgrammeListDetailSerializer
    lookup_field = "pk"

    def get_queryset(self):
        return Programme.objects.prefetch_related("course_set").select_related(
            "school", "department"
        )


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
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseListSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = CourseFilter
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def get(self, request, *args, **kwargs):
        try:
            courses = self.get_queryset()
            courses = self.filter_queryset(courses)
            page = request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_courses = paginator.paginate_queryset(courses, request)
                serializer = self.get_serializer(paginated_courses, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseCreateSerializer
    lookup_field = "pk"
    http_method_names = ["patch", "delete"]

    def patch(self, request, *args, **kwargs):
        try:
            return super().patch(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SemesterCreateView(generics.CreateAPIView):
    queryset = Semester.objects.all()
    serializer_class = SemesterCreateSerializer

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            academic_year_id = data.get("academic_year")
            name = data.get("name")

            # Duplicate check (same name in same academic_year)
            if Semester.objects.filter(
                name__iexact=name, academic_year_id=academic_year_id
            ).exists():
                return Response(
                    {
                        "success": False,
                        "error": "A semester with this name already exists in the selected Academic Year.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as exc:
            # logger.error(f"Error creating Semester: {exc}")
            return Response(
                {"success": False, "error": f"Internal server error: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SemesterDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Semester.objects.all()
    serializer_class = SemesterCreateSerializer
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            data = request.data
            academic_year_id = data.get("academic_year", instance.academic_year_id)
            name = data.get("name", instance.name)

            # Duplicate check excluding current
            if (
                Semester.objects.exclude(pk=instance.pk)
                .filter(name__iexact=name, academic_year_id=academic_year_id)
                .exists()
            ):
                return Response(
                    {
                        "success": False,
                        "error": "Another semester with this name already exists in the selected Academic Year.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            # logger.error(f"Error updating Semester: {exc}")
            return Response(
                {"success": False, "error": f"Internal server error: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return Response(
                {"success": True, "message": "Semester deleted successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            # logger.error(f"Error deleting Semester: {exc}")
            return Response(
                {"success": False, "error": f"Internal server error: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SemesterListView(generics.ListAPIView):
    queryset = Semester.objects.all().order_by("-created_on")
    serializer_class = SemesterListSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = SemesterFilter
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def get(self, request, *args, **kwargs):
        try:
            semesters = self.get_queryset()
            semesters = self.filter_queryset(semesters)
            page = request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_semesters = paginator.paginate_queryset(semesters, request)
                serializer = self.get_serializer(paginated_semesters, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(semesters, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response(
                {"success": False, "error": f"Internal server error: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProgrammeCohortListView(generics.ListAPIView):
    queryset = ProgrammeCohort.objects.all()
    serializer_class = ProgrammeCohortListSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = CohortsFilter
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def get(self, request, *args, **kwargs):
        try:
            cohorts = self.get_queryset()
            cohorts = self.filter_queryset(cohorts)
            page = request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_schools = paginator.paginate_queryset(cohorts, request)
                serializer = self.get_serializer(paginated_schools, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(cohorts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProgrammeCohortUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProgrammeCohort.objects.all()
    serializer_class = ProgrammeCohortCreateSerializer
    lookup_field = "pk"
    http_method_names = ["patch", "delete"]

    def patch(self, request, *args, **kwargs):
        try:
            return super().patch(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseSessionListView(generics.ListAPIView):
    queryset = CourseSession.objects.all()
    serializer_class = CourseSessionListSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = CourseSessionFilter
    permission_classes = [IsAuthenticated]

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
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseSessionUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CourseSession.objects.all()
    serializer_class = CourseSessionCreateSerializer
    lookup_field = "pk"
    http_method_names = ["patch", "delete"]

    def patch(self, request, *args, **kwargs):
        try:
            return super().patch(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
