from django.contrib import admin

from apps.finance.models import Payment, LibraryFinePayment, FeePayment, Budget, BudgetDocument


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

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "amount_requested", "amount_approved", "status"]


@admin.register(BudgetDocument)
class BudgetDocumentAdmin(admin.ModelAdmin):
    list_display = ["id", "budget", "document_name", "document_file"]