from django.contrib import admin

from apps.finance.models import Payment, LibraryFinePayment, FeePayment, FeeStructureItem


# Register your models here.
@admin.register(LibraryFinePayment)
class LibraryFinePaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "member",
        "fine",
        "amount",
        "payment_date",
        "payment_method",
        "payment_reference",
        "paid",
    )

@admin.register(FeeStructureItem)
class FeeStructureItemAdmin(admin.ModelAdmin):
    list_display = ["id", "fee_structure", "description", "amount"]