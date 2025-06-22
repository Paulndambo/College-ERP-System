from django.contrib import admin
from apps.student_finance.models import (
    StudentFeeInvoice,
    StudentFeePayment,
    StudentFeeLedger,
    StudentFeeStatement,
)


# Register your models here.
@admin.register(StudentFeeInvoice)
class StudentFeeInvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "description",
        "reference",
        "semester",
        "amount",
        "amount_paid",
        "status",
        "created_on",
        "bal_due"
    )


@admin.register(StudentFeePayment)
class StudentFeePaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "amount",
        "payment_date",
        "payment_method",
        "created_on",
    )
  

@admin.register(StudentFeeLedger)
class StudentFeeLedgerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "transaction_type",
        "credit",
        "debit",
        "created_on",
    )


@admin.register(StudentFeeStatement)
class StudentFeeStatementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "statement_type",
        "transaction_type",
        "semester",
        "academic_year",
        "debit",
        "credit",
        "balance",
        "created_on",
    )
