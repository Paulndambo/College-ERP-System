from django.contrib import admin

from apps.inventory.models import UnitOfMeasure
from apps.procurement.models import (
    GoodsReceived,
    PurchaseItem,
    PurchaseOrder,
    Tender,
    TenderApplication,
    TenderAward,
    Vendor,
    VendorPayment,
)


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "deadline",
        "created_by",
        "status",
        "projected_amount",
        "actual_amount",
        "tender_document",
        "start_date",
        "end_date",
    )
    search_fields = ("title", "description")
    list_filter = ("start_date", "start_date", "deadline", "status")


@admin.register(TenderApplication)
class TenderApplicationAdmin(admin.ModelAdmin):
    list_display = ("company_name", "tender", "status")
    search_fields = ("company_name", "tender__title")
    list_filter = ("status", "tender__created_by")


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = (
        "vendor_no",
        "name",
        "email",
        "phone",
        "address",
        "contact_person",
        "contact_person_phone",
        "contact_person_email",
        "status",
        "created_on",
        "updated_on",
        "business_type",
        "tax_pin",
        "company_registration_number",
    )
    search_fields = ("name", "email", "phone", "address")
    list_filter = ("name", "email", "phone", "address")


@admin.register(TenderAward)
class TenderAwardAdmin(admin.ModelAdmin):
    list_display = ("tender", "vendor", "award_amount", "status")
    search_fields = ("tender__title", "vendor__name")
    list_filter = ("tender__created_by", "vendor__name")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("tender", "vendor")


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("vendor", "status", "created_by")
    list_filter = ("status",)


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = (
        "purchase_order",
        "name",
        "quantity",
        "unit",
        "unit_price",
        "total_price",
    )
    search_fields = ("purchase_order__tender__title", "name")
    list_filter = ("purchase_order__vendor__name",)


@admin.register(GoodsReceived)
class GoodsReceivedAdmin(admin.ModelAdmin):
    list_display = (
        "purchase_order",
        "remarks",
    )
    search_fields = ("purchase_order__tender__title", "remarks")
    list_filter = ("purchase_order__vendor__name",)


@admin.register(VendorPayment)
class VendorPaymentAdmin(admin.ModelAdmin):
    list_display = ("amount", "created_on")
