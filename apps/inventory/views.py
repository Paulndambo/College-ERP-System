from rest_framework import generics, permissions
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
import logging
from apps.accounting.models import Account
from apps.inventory.flters import InventoryItemFilter
from apps.inventory.models import Category, InventoryItem, UnitOfMeasure, StockIssue
from apps.inventory.serializers import (
    CategoryListSerializer,
    CreateCategorySerializer,
    CreateInventoryItemSerializer,
    CreateUnitOfMeasureSerializer,
    InventoryItemListSerializer,
    UnitOfMeasureListSerializer,
)

logger = logging.getLogger(__name__)


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
                paginated_qs = paginator.paginate_queryset(qs, request)
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
                paginated_qs = paginator.paginate_queryset(qs, request)
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
                paginated_qs = paginator.paginate_queryset(qs, request)
                serializer = self.get_serializer(paginated_qs, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response(str(exc), status=status.HTTP_400_BAD_REQUEST)


class CreateInventoryItemAPIView(generics.CreateAPIView):
    queryset = InventoryItem.objects.all()
    serializer_class = CreateInventoryItemSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check for duplicate inventory item
            name = serializer.validated_data.get("name", "").strip()
            category = serializer.validated_data.get("category")

            # Case-insensitive check for existing item with same name and category
            existing_item = InventoryItem.objects.filter(
                name__iexact=name, category=category
            ).exists()

            if existing_item:
                return Response(
                    {
                        "error": "Inventory Item with given name already exists for the given category.You might consider updating the existing item instead."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create new item if no duplicate found
            instance = serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InventoryItemDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InventoryItem.objects.all()
    serializer_class = CreateInventoryItemSerializer
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Store original values before update
        original_quantity = instance.quantity_in_stock
        original_unit_valuation = instance.unit_valuation or Decimal("0.00")
        original_total_valuation = instance.total_valuation or Decimal("0.00")
        original_unit = instance.unit

        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            # Check for duplicate inventory item (excluding current instance)
            name = serializer.validated_data.get("name", instance.name).strip()
            category = serializer.validated_data.get("category", instance.category)

            # Case-insensitive check for existing item with same name and category
            existing_item = (
                InventoryItem.objects.filter(name__iexact=name, category=category)
                .exclude(pk=instance.pk)
                .exists()
            )

            if existing_item:
                return Response(
                    {
                        "error": "Inventory Item with given name already exists for the given category"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update the instance
            updated_instance = serializer.save()

            # Get new values after update
            new_quantity = updated_instance.quantity_in_stock
            new_unit_valuation = updated_instance.unit_valuation or Decimal("0.00")
            new_total_valuation = updated_instance.total_valuation or Decimal("0.00")
            new_unit = updated_instance.unit

            # Check if there are changes in quantity, unit_valuation, total_valuation, or unit
            changes_detected = (
                original_quantity != new_quantity
                or original_unit_valuation != new_unit_valuation
                or original_total_valuation != new_total_valuation
                or original_unit != new_unit
            )

            if changes_detected:
                # Calculate the difference in total valuation
                valuation_difference = new_total_valuation - original_total_valuation

                # Create journal entry for the difference
                self.create_inventory_adjustment_journal(
                    instance=updated_instance,
                    valuation_difference=valuation_difference,
                    original_values={
                        "quantity": original_quantity,
                        "unit_valuation": original_unit_valuation,
                        "total_valuation": original_total_valuation,
                        "unit": original_unit.name if original_unit else None,
                    },
                    new_values={
                        "quantity": new_quantity,
                        "unit_valuation": new_unit_valuation,
                        "total_valuation": new_total_valuation,
                        "unit": new_unit.name if new_unit else None,
                    },
                )

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create_inventory_adjustment_journal(
        self, instance, valuation_difference, original_values, new_values
    ):
        """Create journal entry for inventory adjustments"""
        if valuation_difference == 0:
            logger.info(
                f"[InventoryItem:{instance.id}] No valuation change — skipping journal entry."
            )
            return

        try:
            inventory_acc = Account.objects.get(name="Inventory")
            # Use appropriate account based on increase or decrease
            if valuation_difference > 0:
                # Inventory increase - credit Cash or Accounts Payable
                contra_acc = Account.objects.get(name="Cash")
                adjustment_type = "Increase"
            else:
                # Inventory decrease - debit Cost of Goods Sold or Inventory Adjustment
                try:
                    contra_acc = Account.objects.get(name="Cost of Goods Sold")
                except Account.DoesNotExist:
                    contra_acc = Account.objects.get(name="Inventory Adjustment")
                adjustment_type = "Decrease"

            logger.info(
                f"[InventoryItem:{instance.id}] Accounts found for {adjustment_type}"
            )
        except Account.DoesNotExist as e:
            logger.error(
                f"[InventoryItem:{instance.id}] Required accounts not found: {e}"
            )
            return

        # Create description with change details
        change_details = []
        if original_values["quantity"] != new_values["quantity"]:
            change_details.append(
                f"Qty: {original_values['quantity']} → {new_values['quantity']}"
            )
        if original_values["unit_valuation"] != new_values["unit_valuation"]:
            change_details.append(
                f"Unit Val: {original_values['unit_valuation']} → {new_values['unit_valuation']}"
            )
        if original_values["unit"] != new_values["unit"]:
            change_details.append(
                f"Unit: {original_values['unit']} → {new_values['unit']}"
            )

        description = (
            f"Inventory Adjustment: {instance.name} ({', '.join(change_details)})"
        )

        # Prepare transactions based on valuation difference
        if valuation_difference > 0:
            # Inventory increased
            transactions = [
                {
                    "account": inventory_acc,
                    "amount": abs(valuation_difference),
                    "is_debit": True,
                },
                {
                    "account": contra_acc,
                    "amount": abs(valuation_difference),
                    "is_debit": False,
                },
            ]
        else:
            # Inventory decreased
            transactions = [
                {
                    "account": contra_acc,
                    "amount": abs(valuation_difference),
                    "is_debit": True,
                },
                {
                    "account": inventory_acc,
                    "amount": abs(valuation_difference),
                    "is_debit": False,
                },
            ]

        # Create journal entry (assuming you have this function)
        try:
            from apps.accounting.services.journals import create_journal_entry

            create_journal_entry(
                description=description,
                reference=f"INVADJ-{instance.id}",
                user=getattr(instance, "updated_by", None),
                transactions=transactions,
            )

            logger.info(
                f"[InventoryItem:{instance.id}] Adjustment journal entry created: {valuation_difference}"
            )
        except Exception as e:
            logger.error(
                f"[InventoryItem:{instance.id}] Failed to create journal entry: {e}"
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if StockIssue.objects.filter(inventory_item=instance).exists():
            return Response(
                {
                    "error": "Cannot delete this inventory item because it has issued stock records."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if instance.quantity_in_stock > 0:
            return Response(
                {"error": "Cannot delete an inventory item that still has stock."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().destroy(request, *args, **kwargs)


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
                {
                    "error": "Cannot delete this unit of measure because it is used in one or more inventory items."
                },
                status=status.HTTP_400_BAD_REQUEST,
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
                {
                    "error": "Cannot delete this category because it is used in one or more inventory items."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().destroy(request, *args, **kwargs)
