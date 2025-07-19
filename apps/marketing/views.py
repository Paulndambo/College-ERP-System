from rest_framework import generics, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from services.constants import ALL_STAFF_ROLES
from services.permissions import HasUserRole

from .models import Lead, Interaction, Campaign, Task, LeadStage
from .serializers import (
    LeadCreateSerializer,
    LeadListDetailSerializer,
    InteractionCreateSerializer,
    InteractionListDetailSerializer,
    CampaignCreateSerializer,
    CampaignListDetailSerializer,
    TaskCreateSerializer,
    TaskListDetailSerializer,
    LeadStageCreateSerializer,
    LeadStageListDetailSerializer,
)

from apps.core.exceptions import CustomAPIException


class LeadCreateView(generics.CreateAPIView):
    queryset = Lead.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = LeadCreateSerializer

    def perform_create(self, serializer):
        if "assigned_to" not in self.request.data:
            serializer.save(assigned_to=self.request.user)
        else:
            serializer.save()


class LeadUpdateView(generics.UpdateAPIView):
    queryset = Lead.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = LeadCreateSerializer
    lookup_field = "pk"

    def patch(self, request, *args, **kwargs):
        lead = self.get_object()
        serializer = self.get_serializer(lead, data=request.data, partial=True)

        if serializer.is_valid():
            if "status" in request.data and request.data["status"] != lead.status:
                LeadStage.objects.create(
                    lead=lead, stage=request.data["status"], added_by=request.user
                )

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeadListView(generics.ListAPIView):
    queryset = Lead.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = LeadListDetailSerializer
    pagination_class = None
    # filter_backends = [
    #     DjangoFilterBackend,
    #     filters.SearchFilter,
    #     filters.OrderingFilter,
    # ]
    # filterset_class = LeadFilter
    # search_fields = ["first_name", "last_name", "email", "phone_number"]
    # ordering_fields = ["created_on", "score", "status"]

    def get_queryset(self):
        queryset = (
            Lead.objects.all()
            .select_related("programme", "assigned_to", "campaign")
            .order_by("-created_on")
        )

        user_id = self.request.query_params.get("assigned_to", None)
        if user_id and user_id.isdigit():
            queryset = queryset.filter(assigned_to_id=int(user_id))

        return queryset

    def list(self, request, *args, **kwargs):
        try:
            leads = self.get_queryset()
            leads = self.filter_queryset(leads)

            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_leads = paginator.paginate_queryset(leads, request)
                serializer = self.get_serializer(paginated_leads, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(leads, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LeadDetailView(generics.RetrieveAPIView):
    queryset = Lead.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = LeadListDetailSerializer
    lookup_field = "pk"


# ================ Interaction Views ================


class InteractionCreateView(generics.CreateAPIView):
    queryset = Interaction.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = InteractionCreateSerializer

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)


class InteractionUpdateView(generics.UpdateAPIView):
    queryset = Interaction.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = InteractionCreateSerializer
    lookup_field = "pk"

    def patch(self, request, *args, **kwargs):
        interaction = self.get_object()
        serializer = self.get_serializer(interaction, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InteractionListView(generics.ListAPIView):
    queryset = Interaction.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = InteractionListDetailSerializer
    pagination_class = None
    # filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    # filterset_class = InteractionFilter
    # ordering_fields = ["date", "created_on"]

    def get_queryset(self):
        queryset = (
            Interaction.objects.all()
            .select_related("lead", "added_by")
            .order_by("-date")
        )

        lead_id = self.request.query_params.get("lead", None)
        if lead_id and lead_id.isdigit():
            queryset = queryset.filter(lead_id=int(lead_id))

        return queryset

    def list(self, request, *args, **kwargs):
        try:
            interactions = self.get_queryset()
            interactions = self.filter_queryset(interactions)

            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_interactions = paginator.paginate_queryset(
                    interactions, request
                )
                serializer = self.get_serializer(paginated_interactions, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(interactions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InteractionDetailView(generics.RetrieveAPIView):
    queryset = Interaction.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = InteractionListDetailSerializer
    lookup_field = "pk"


# ================ Campaign Views ================


class CampaignCreateView(generics.CreateAPIView):
    queryset = Campaign.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = CampaignCreateSerializer

    def perform_create(self, serializer):
        serializer.save()


class CampaignUpdateView(generics.UpdateAPIView):
    queryset = Campaign.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = CampaignCreateSerializer
    lookup_field = "pk"

    def patch(self, request, *args, **kwargs):
        campaign = self.get_object()
        serializer = self.get_serializer(campaign, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CampaignListView(generics.ListAPIView):
    queryset = Campaign.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = CampaignListDetailSerializer
    pagination_class = None
    # filter_backends = [
    #     DjangoFilterBackend,
    #     filters.SearchFilter,
    #     filters.OrderingFilter,
    # ]
    # filterset_class = CampaignFilter
    # search_fields = ["name", "description"]
    # ordering_fields = ["start_date", "end_date", "created_on"]

    def get_queryset(self):
        return Campaign.objects.all().order_by("-start_date")

    def list(self, request, *args, **kwargs):
        try:
            campaigns = self.get_queryset()
            campaigns = self.filter_queryset(campaigns)

            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_campaigns = paginator.paginate_queryset(campaigns, request)
                serializer = self.get_serializer(paginated_campaigns, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(campaigns, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CampaignDetailView(generics.RetrieveAPIView):
    queryset = Campaign.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = CampaignListDetailSerializer
    lookup_field = "slug"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count on retrieval
        instance.views += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# ================ Task Views ================


class TaskCreateView(generics.CreateAPIView):
    queryset = Task.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = TaskCreateSerializer

    def perform_create(self, serializer):
        # If user not specified, assign to current user
        if "user" not in self.request.data:
            serializer.save(user=self.request.user)
        else:
            serializer.save()


class TaskUpdateView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = TaskCreateSerializer
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return Task.objects.none()
        # Users can only update their own tasks unless they're in ALL_STAFF_ROLES
        if user.role.name in ALL_STAFF_ROLES:
            return Task.objects.all()
        return Task.objects.filter(user=user)

    def patch(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskListView(generics.ListAPIView):
    queryset = Task.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = TaskListDetailSerializer
    pagination_class = None
    # filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    # filterset_class = TaskFilter
    # ordering_fields = ["due_date", "created_on"]

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.all().select_related("user", "lead")

        my_tasks_only = self.request.query_params.get("my_tasks", None)
        if my_tasks_only == "true":
            queryset = queryset.filter(user=user)

        lead_id = self.request.query_params.get("lead", None)
        if lead_id and lead_id.isdigit():
            queryset = queryset.filter(lead_id=int(lead_id))

        completed = self.request.query_params.get("completed", None)
        if completed in ["true", "false"]:
            queryset = queryset.filter(completed=(completed == "true"))

        due_filter = self.request.query_params.get("due", None)
        today = timezone.now().date()

        if due_filter == "today":
            queryset = queryset.filter(due_date__date=today)
        elif due_filter == "upcoming":
            queryset = queryset.filter(due_date__date__gt=today)
        elif due_filter == "overdue":
            queryset = queryset.filter(due_date__date__lt=today, completed=False)

        return queryset.order_by("due_date")

    def list(self, request, *args, **kwargs):
        try:
            tasks = self.get_queryset()
            tasks = self.filter_queryset(tasks)

            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_tasks = paginator.paginate_queryset(tasks, request)
                serializer = self.get_serializer(paginated_tasks, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(tasks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TaskDetailView(generics.RetrieveAPIView):
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = TaskListDetailSerializer
    lookup_field = "pk"

    def get_queryset(self):
        user = self.request.user
        if isinstance(user, AnonymousUser):
            return Task.objects.none()
        if user.role.name in ALL_STAFF_ROLES:
            return Task.objects.all()
        return Task.objects.filter(user=user)


# ================ LeadStage Views ================


class LeadStageCreateView(generics.CreateAPIView):
    queryset = LeadStage.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = LeadStageCreateSerializer

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)


class LeadStageUpdateView(generics.UpdateAPIView):
    queryset = LeadStage.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = LeadStageCreateSerializer
    lookup_field = "pk"

    def patch(self, request, *args, **kwargs):
        lead_stage = self.get_object()
        serializer = self.get_serializer(lead_stage, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeadStageListView(generics.ListAPIView):
    queryset = LeadStage.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = LeadStageListDetailSerializer
    pagination_class = None
    # filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    # filterset_class = LeadStageFilter
    # ordering_fields = ["date_reached", "created_on"]

    def get_queryset(self):
        queryset = LeadStage.objects.all().select_related("lead", "added_by")

        # Filter by lead if specified
        lead_id = self.request.query_params.get("lead", None)
        if lead_id and lead_id.isdigit():
            queryset = queryset.filter(lead_id=int(lead_id))

        return queryset.order_by("-date_reached")

    def list(self, request, *args, **kwargs):
        try:
            stages = self.get_queryset()
            stages = self.filter_queryset(stages)

            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_stages = paginator.paginate_queryset(stages, request)
                serializer = self.get_serializer(paginated_stages, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(stages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LeadStageDetailView(generics.RetrieveAPIView):
    queryset = LeadStage.objects.all()
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    serializer_class = LeadStageListDetailSerializer
    lookup_field = "pk"
