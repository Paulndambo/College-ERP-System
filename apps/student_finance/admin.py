from django.contrib import admin
from apps.student_finance.models import StudentFeeInvoice, StudentFeePayment, StudentFeeLedger
# Register your models here.
@admin.register(StudentFeeInvoice)
class StudentFeeInvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "description", "semester", "amount", "amount_paid", "status")
    
    
@admin.register(StudentFeePayment)
class StudentFeePaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "amount", "payment_date", "payment_method")
    

@admin.register(StudentFeeLedger)
class StudentFeeLedgerAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "transaction_type", "credit", "debit", "balance")