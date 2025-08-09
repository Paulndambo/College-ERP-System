from django.db import models
from apps.core.models import AbsoluteBaseModel
from apps.procurement.models import PurchaseOrder, Vendor
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

CATEGORY_TYPE_CHOICES = [
    ("fixed_asset", "Fixed Asset"),
    ("inventory", "Inventory"),
    ("consumable", "Consumable"),
    ("service", "Service"),
    ("other", "Other"),
]


class Category(AbsoluteBaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category_type = models.CharField(
        max_length=20,
        choices=CATEGORY_TYPE_CHOICES,
        default="inventory",
    )

    def __str__(self):
        return self.name


class UnitOfMeasure(AbsoluteBaseModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class InventoryItem(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        "Category", on_delete=models.SET_NULL, null=True, blank=True
    )

    quantity_in_stock = models.PositiveIntegerField(default=0)
    unit = models.ForeignKey(UnitOfMeasure, on_delete=models.SET_NULL, null=True)
    unit_valuation = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        default=0.00,
        help_text="Cost per unit (for inventory items)",
    )
    total_valuation = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        default=0.00,
        help_text="Total value (for fixed assets or special cases)",
    )

    def effective_total_valuation(self):
        """Return calculated total if unit_valuation is used, else fall back to stored total_valuation"""
        if self.unit_valuation is not None:
            return self.quantity_in_stock * self.unit_valuation
        return self.total_valuation

    def __str__(self):
        return f"{self.name} ({self.quantity_in_stock} {self.unit})"


class StockReceipt(AbsoluteBaseModel):
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True
    )
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)

    quantity_received = models.PositiveIntegerField()
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.quantity_received} {self.inventory_item.unit} received of {self.inventory_item.name}"


class StockIssue(AbsoluteBaseModel):
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    issued_to = models.ForeignKey(
        "schools.Department",
        on_delete=models.SET_NULL,
        null=True,
        help_text="Department that received the stock",
    )
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    remarks = models.TextField(blank=True)
    issued_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Issued {self.quantity} {self.inventory_item.unit} of {self.inventory_item.name} to {self.issued_to}"
