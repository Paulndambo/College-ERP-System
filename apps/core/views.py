from django.forms import ValidationError
from apps.core.filters import AcademicYearsFilter, CampusFilter
from rest_framework import generics, status
from rest_framework.response import Response
from apps.core.base_api_error_exceptions.base_exceptions import CustomAPIException
from apps.core.utils import ModelCountUtils
from services.constants import ALL_STAFF_ROLES
from services.permissions import HasUserRole
from django.contrib.admin.models import LogEntry
from .serializers import LogEntrySerializer, ModuleSerializer, RoleSerializer
from .models import Campus, Module, StudyYear, UserRole
from .serializers import (
    CampusCreateSerializer,
    CampusListSerializer,
    StudyYearCreateSerializer,
    StudyYearListSerializer,
    UserRoleListSerializer,
)
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


# class UserRoleListView(generics.ListAPIView):
#     queryset = UserRole.objects.all()
#     serializer_class = UserRoleListSerializer
#     permission_classes = [HasUserRole]
#     allowed_roles = ALL_STAFF_ROLES
#     filter_backends = [DjangoFilterBackend]

#     pagination_class = None

#     def get_queryset(self):
#         return UserRole.objects.all().order_by("-created_on")

    # def get_paginated_response(self, data):
    #     return super().get_paginated_response(data)

    # def list(self, request, *args, **kwargs):
    #     try:
    #         roles = self.get_queryset()
    #         roles = self.filter_queryset(roles)
    #         page = self.request.query_params.get("page", None)
    #         if page:
    #             self.pagination_class = PageNumberPagination
    #             paginator = self.pagination_class()
    #             paginated_roles = paginator.paginate_queryset(roles, request)
    #             serializer = self.get_serializer(paginated_roles, many=True)
    #             return paginator.get_paginated_response(serializer.data)

    #         serializer = self.get_serializer(roles, many=True)
    #         return Response(serializer.data, status=status.HTTP_200_OK)

    #     except Exception as exc:
    #         raise CustomAPIException(
    #             message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    #         )


class CampusCreateView(generics.CreateAPIView):
    queryset = Campus.objects.all()
    serializer_class = CampusCreateSerializer

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


class CampusListView(generics.ListAPIView):
    queryset = Campus.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = CampusListSerializer
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = CampusFilter
    pagination_class = None

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def get(self, request, *args, **kwargs):
        try:
            campuses = self.get_queryset()
            campuses = self.filter_queryset(campuses)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_campuses = paginator.paginate_queryset(campuses, request)
                serializer = self.get_serializer(paginated_campuses, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(campuses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class CampusUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Campus.objects.all()
    serializer_class = CampusCreateSerializer
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


class StudyYearCreateView(generics.CreateAPIView):
    queryset = StudyYear.objects.all()
    serializer_class = StudyYearCreateSerializer

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


class StudyYearListView(generics.ListAPIView):
    queryset = StudyYear.objects.all()
    serializer_class = StudyYearListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AcademicYearsFilter
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            study_years = self.get_queryset()
            study_years = self.filter_queryset(study_years)
            page = request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_study_years = paginator.paginate_queryset(
                    study_years, request
                )
                serializer = self.get_serializer(paginated_study_years, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(study_years, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StudyYearUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudyYear.objects.all()
    serializer_class = StudyYearCreateSerializer
    lookup_field = "pk"
    http_method_names = ["patch", "delete"]
    permission_classes = [IsAuthenticated]

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


class DashboardCountsRetrieveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            data = ModelCountUtils.get_all_counts()
            return Response(
                {
                    "success": True,
                    "data": data,
                    "message": "Dashboard counts retrieved successfully",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            raise NotFound(f"Dashboard counts not available: {str(e)}")


class RecentActionsView(APIView):

    def get(self, request):
        logs = LogEntry.objects.select_related("user", "content_type").order_by(
            "-action_time"
        )[:50]
        serializer = LogEntrySerializer(logs, many=True)
        return Response(serializer.data)





class RolesListAPIView(generics.ListAPIView):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleListSerializer
    def get_paginated_response(self, data):
        return super().get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            roles = self.get_queryset()
            roles = self.filter_queryset(roles)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_roles = paginator.paginate_queryset(roles, request)
                serializer = self.get_serializer(paginated_roles, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(roles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RoleListCreateView(generics.CreateAPIView):
    queryset = UserRole.objects.all()
    serializer_class = RoleSerializer

    def perform_create(self, serializer):
        name = serializer.validated_data.get('name')
        if UserRole.objects.filter(name__iexact=name).exists():
            raise ValidationError({"error": "A role with this name already exists."})
        serializer.save()


class RoleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserRole.objects.all()
    serializer_class = RoleSerializer

    def perform_update(self, serializer):
        name = serializer.validated_data.get('name')
        instance_id = self.get_object().id
        if UserRole.objects.filter(name__iexact=name).exclude(id=instance_id).exists():
            raise ValidationError({"error": "A role with this name already exists."})
        serializer.save()
class ModulesListView(generics.ListAPIView):
    queryset = Module.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ModuleSerializer
    pagination_class = None

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def get(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            qs = self.filter_queryset(qs)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_modules = paginator.paginate_queryset(qs, request)
                serializer = self.get_serializer(paginated_modules, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
