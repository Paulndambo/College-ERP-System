from rest_framework import generics,permissions
from django.db import transaction

from django.shortcuts import get_object_or_404

from rest_framework.pagination import PageNumberPagination

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from apps.inventory.flters import InventoryItemFilter
from apps.inventory.models import Category, InventoryItem, UnitOfMeasure
from apps.inventory.serializers import CategoryListSerializer, CreateCategorySerializer, CreateUnitOfMeasureSerializer, InventoryItemListSerializer, UnitOfMeasureListSerializer




class UnitOfMeasureAPIView(generics.ListAPIView):
    queryset = UnitOfMeasure.objects.all().order_by("-created_on")
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UnitOfMeasureListSerializer
    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            qs = self.filter_queryset(qs)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_qs = paginator.paginate_queryset(
                    qs, request
                )
                serializer = self.get_serializer(paginated_qs, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response(str(exc), status=status.HTTP_400_BAD_REQUEST)


class CategoriesAPIView(generics.ListAPIView):
    queryset = Category.objects.all().order_by("-created_on")
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CategoryListSerializer
    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            qs = self.filter_queryset(qs)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_qs = paginator.paginate_queryset(
                    qs, request
                )
                serializer = self.get_serializer(paginated_qs, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response(str(exc), status=status.HTTP_400_BAD_REQUEST)


class InventoryItemsListView(generics.ListAPIView):
    queryset = InventoryItem.objects.all().order_by("-created_on")
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InventoryItemListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = InventoryItemFilter
    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            qs = self.get_queryset()
            qs = self.filter_queryset(qs)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_qs = paginator.paginate_queryset(
                    qs, request
                )
                serializer = self.get_serializer(paginated_qs, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response(str(exc), status=status.HTTP_400_BAD_REQUEST)


class CreateCategoryAPIView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CreateCategorySerializer
class CreateUnitOfMeasureAPIView(generics.CreateAPIView):
    queryset = UnitOfMeasure.objects.all()
    serializer_class = CreateUnitOfMeasureSerializer
class UnitOfMeasureDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UnitOfMeasure.objects.all()
    serializer_class = CreateUnitOfMeasureSerializer
    lookup_field = "pk"
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.inventoryitem_set.exists():
            return Response(
                {"error": "Cannot delete this unit of measure because it is used in one or more inventory items."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().destroy(request, *args, **kwargs)
    
class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CreateCategorySerializer
    lookup_field = "pk"
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.inventoryitem_set.exists():
            return Response(
                {"error": "Cannot delete this category because it is used in one or more inventory items."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)