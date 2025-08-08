from datetime import datetime, timedelta
import calendar
from rest_framework.pagination import PageNumberPagination

from decimal import Decimal
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.db.models import Q, Sum
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from django.db import transaction

from django.views.generic import ListView
from django.http import JsonResponse
from rest_framework import generics, status
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.base_api_error_exceptions.base_exceptions import CustomAPIException
from apps.finance.filters import FeeStructureFilter
from apps.finance.serializers import (
    FeeStructureCreateUpdateSerializer,
    FeeStructureItemCreateUpdateSerializer,
    FeeStructureItemListSerializer,
    FeeStructureListSerializer,
)
from .models import FeeStructure, FeeStructureItem
from apps.finance.models import LibraryFinePayment, Payment, FeePayment, Budget
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

date_today = datetime.now().date()


class FeeStructureListView(generics.ListAPIView):
    queryset = (
        FeeStructure.objects.prefetch_related("feeitems").all().order_by("-created_on")
    )
    serializer_class = FeeStructureListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = FeeStructureFilter
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            fee_structures = self.get_queryset()
            fee_structures = self.filter_queryset(fee_structures)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_fee_structures = paginator.paginate_queryset(
                    fee_structures, request
                )
                serializer = self.get_serializer(paginated_fee_structures, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(fee_structures, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FeeStructureRetrieveView(generics.RetrieveAPIView):
    queryset = FeeStructure.objects.prefetch_related("feeitems").all()
    serializer_class = FeeStructureListSerializer
    lookup_field = "id"
    permission_classes = [IsAuthenticated]


class FeeStructureCreateView(generics.CreateAPIView):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureCreateUpdateSerializer


class FeeStructureUpdateView(generics.UpdateAPIView):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureCreateUpdateSerializer
    lookup_field = "id"


class FeeStructureDeleteView(generics.DestroyAPIView):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureCreateUpdateSerializer
    lookup_field = "id"


class FeeStructureItemListView(generics.ListAPIView):
    serializer_class = FeeStructureItemListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        fee_structure_id = self.request.query_params.get("fee_structure")
        if fee_structure_id:
            return FeeStructureItem.objects.filter(fee_structure_id=fee_structure_id)
        return FeeStructureItem.objects.none()


class FeeStructureItemByStructureView(generics.ListAPIView):
    serializer_class = FeeStructureItemListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        fee_structure_id = self.kwargs.get("fee_structure_id")
        if not fee_structure_id:
            raise ValidationError("FeeStructure ID is required")

        queryset = FeeStructureItem.objects.filter(fee_structure_id=fee_structure_id)

        semester = self.request.query_params.get("semester")
        year_of_study = self.request.query_params.get("year_of_study")

        if semester:
            queryset = queryset.filter(fee_structure__semester_id=semester)

        if year_of_study:
            queryset = queryset.filter(fee_structure__year_of_study_id=year_of_study)

        return queryset

    def list(self, request, *args, **kwargs):
        fee_structure_id = kwargs.get("fee_structure_id")
        if not fee_structure_id:
            raise ValidationError("FeeStructure  is required")
        try:
            fee_structure = FeeStructure.objects.get(id=fee_structure_id)
        except FeeStructure.DoesNotExist:
            raise ValidationError("FeeStructure not found")

        queryset = self.filter_queryset(self.get_queryset())
        total_amount = queryset.aggregate(total=Sum("amount"))["total"] or 0
        page = self.paginate_queryset(queryset)

        if page is not None:
            serialized_page = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serialized_page.data)
            paginated_response.data["fee_structure"] = FeeStructureListSerializer(
                fee_structure
            ).data
            paginated_response.data["total_amount"] = total_amount
            return paginated_response

        serialized = self.get_serializer(queryset, many=True)
        return Response(
            {
                "fee_structure": FeeStructureSerializer(fee_structure).data,
                "total_amount": total_amount,
                "results": serialized.data,
            }
        )


class FeeStructureItemRetrieveView(generics.RetrieveAPIView):
    queryset = FeeStructureItem.objects.all()
    serializer_class = FeeStructureItemListSerializer
    lookup_field = "id"


class FeeStructureItemCreateView(generics.CreateAPIView):
    queryset = FeeStructureItem.objects.all()
    serializer_class = FeeStructureItemCreateUpdateSerializer


class FeeStructureItemUpdateView(generics.UpdateAPIView):
    queryset = FeeStructureItem.objects.all()
    serializer_class = FeeStructureItemCreateUpdateSerializer
    lookup_field = "id"


class FeeStructureItemDeleteView(generics.DestroyAPIView):
    queryset = FeeStructureItem.objects.all()
    serializer_class = FeeStructureItemCreateUpdateSerializer
    lookup_field = "id"
