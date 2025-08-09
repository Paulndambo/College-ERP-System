from django.contrib import admin

from apps.payroll.models import PaymentStatement


# Register your models here.
@admin.register(PaymentStatement)
class PaymentStatementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "payslip",
        "total_amount_due",
        "total_amount_paid",
        "outstanding_balance",
        "created_at",
        "updated_at",
    )
