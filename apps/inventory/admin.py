from django.contrib import admin

from apps.inventory.models import Category, InventoryItem, StockIssue, StockReceipt, UnitOfMeasure

@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    list_filter = ("name",)


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "category_type")
    search_fields = ("category_type",)

    # def get_queryset(self, request):
    #     return super().get_queryset(request).select_related("parent_category")


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "quantity_in_stock", "unit", "unit_valuation", "total_valuation")
    search_fields = ("name", "category__name")
    list_filter = ("category",)


@admin.register(StockReceipt)
class StockReceiptAdmin(admin.ModelAdmin):
    list_display = (
        "inventory_item",
        "purchase_order",
        "vendor",
        "quantity_received",
        "remarks",
    )
    search_fields = ("inventory_item__name", "vendor__name")
    list_filter = ("vendor",)


@admin.register(StockIssue)
class StockIssueAdmin(admin.ModelAdmin):
    list_display = ("inventory_item", "issued_to", "quantity", "issued_by", "issued_on")
    search_fields = ("inventory_item__name", "issued_to__name")
    list_filter = ("issued_to", "issued_by")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("inventory_item", "issued_to", "issued_by")
        )
