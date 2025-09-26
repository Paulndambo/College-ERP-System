from django.forms import ValidationError
from apps.core.filters import AcademicYearsFilter, CampusFilter
from rest_framework import generics, status
from rest_framework.response import Response
from apps.core.base_api_error_exceptions.base_exceptions import CustomAPIException
from apps.core.utils import ModelCountUtils
from services.constants import ALL_STAFF_ROLES
from services.permissions import HasUserRole
from django.contrib.admin.models import LogEntry
from .serializers import CreateAndUpdateRoleSerializer, LogEntrySerializer, LoggedInPermisionsSerializer, ModuleSerializer, RoleDetailWithPermissionsSerializer, RoleSerializer
from .models import Campus, Module, RolePermission, StudyYear, UserRole
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

class CreateRoleView(generics.CreateAPIView):
    """
    API endpoint to create a UserRole.
    Automatically sets created_by to the current user.
    Returns custom JSON if a role with the same name already exists.
    """

    queryset = UserRole.objects.all()
    serializer_class = CreateAndUpdateRoleSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Check for an existing role with the same name (case-insensitive)
        role_name = request.data.get("name", "").strip()
        if UserRole.objects.filter(name__iexact=role_name).exists():
            return Response(
                {"error": f"A role with the name '{role_name}' already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # If no duplicate, proceed with normal creation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        # Save with created_by filled automatically by the HiddenField
        serializer.save()


class UpdateDeleteRoleView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to update or delete a UserRole.
    Uses pk for lookup and checks for duplicate names on update.
    """

    queryset = UserRole.objects.all()
    serializer_class = CreateAndUpdateRoleSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    http_method_names = ["patch", "put", "delete"]

    def update(self, request, *args, **kwargs):
        # Get the current instance being updated
        instance = self.get_object()
        new_name = request.data.get("name", "").strip()

        # Check for duplicate names excluding this instance
        if (
            UserRole.objects.filter(name__iexact=new_name)
            .exclude(pk=instance.pk)
            .exists()
        ):
            return Response(
                {"error": f"A role with the name '{new_name}' already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Proceed with normal update
        serializer = self.get_serializer(
            instance, data=request.data, partial=kwargs.get("partial", False)
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        # Save the updated role
        serializer.save()
        
class RoleDetailPermissionsView(generics.RetrieveAPIView):
    """
    GET /api/roles/<pk>/permissions/
    Returns role info + ALL modules with current permissions.
    """

    queryset = UserRole.objects.all()
    serializer_class = RoleDetailWithPermissionsSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class UpdateRolePermissionsView(generics.UpdateAPIView):
    """
    PATCH /api/roles/<pk>/permissions/
    Expects: {"permissions": [ {module_id, can_view, ...}, ... ]}
    """

    queryset = UserRole.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        role = self.get_object()
        perms = request.data.get("permissions", [])
        if not isinstance(perms, list):
            return Response({"error": "permissions must be a list"}, status=400)
        sent_module_ids = []
        for p in perms:

            module_id = p.get("module_id")
            if not module_id:
                continue

            sent_module_ids.append(module_id)
            module = Module.objects.filter(pk=module_id).first()
            if not module:
                continue

            obj, created = RolePermission.objects.get_or_create(
                role=role, module=module
            )
            # Update fields
            for field in [
                "can_view",
                "can_create",
                "can_edit",
                "can_delete",
                "can_approve",
                "can_export",
                "can_print",
                "can_view_all",
            ]:
                setattr(obj, field, bool(p.get(field, False)))
            obj.save()
            RolePermission.objects.filter(role=role).exclude(
                module_id__in=sent_module_ids
            ).delete()

        # Return the fresh detail
        serializer = RoleDetailWithPermissionsSerializer(role)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LoggedInPermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = LoggedInPermisionsSerializer(request.user)
        return Response(serializer.data)
