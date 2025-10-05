import logging
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from apps.staff.models import LeavePolicy
from apps.staff.leaves.serializers import (
    LeavePolicyListSerializer,
    CreateAndUpdateLeavePolicySerializer,
)

logger = logging.getLogger(__name__)

# ----------------- LEAVE POLICY -----------------

class CreateLeavePolicyView(generics.CreateAPIView):
    queryset = LeavePolicy.objects.all()
    serializer_class = CreateAndUpdateLeavePolicySerializer

    def create(self, request, *args, **kwargs):
        try:
            name = request.data.get("name")
            if LeavePolicy.objects.filter(name__iexact=name).exists():
                return Response(
                    {"success": False, "error": "LeavePolicy with this name already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # automatically set created_by if needed
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as exc:
            logger.error(f"Error creating LeavePolicy: {exc}")
            return Response(
                {"success": False, "error": f"Internal server error: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LeavePoliciesListView(generics.ListAPIView):
    serializer_class = LeavePolicyListSerializer
    queryset = LeavePolicy.objects.all().order_by("-created_on")

    def get(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            qs = self.filter_queryset(qs)
            page = request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_qs = paginator.paginate_queryset(qs, request)
                serializer = self.get_serializer(paginated_qs, many=True)
                return paginator.get_paginated_response(serializer.data)
            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error listing LeavePolicies: {str(e)}")
            return Response(
                {"success": False, "error": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LeavePolicyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CreateAndUpdateLeavePolicySerializer
    queryset = LeavePolicy.objects.all()
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            name = request.data.get("name")
            if name and LeavePolicy.objects.exclude(id=instance.id).filter(name__iexact=name).exists():
                return Response(
                    {"success": False, "error": "Another LeavePolicy with this name already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()  # created_by not changed
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            logger.error(f"Error updating LeavePolicy: {exc}")
            return Response(
                {"success": False, "error": f"Internal server error: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({"success": True, "message": "LeavePolicy deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as exc:
            logger.error(f"Error deleting LeavePolicy: {exc}")
            return Response(
                {"success": False, "error": f"Internal server error: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
