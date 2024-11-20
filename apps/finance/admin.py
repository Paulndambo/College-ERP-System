from django.contrib import admin

from apps.finance.models import Payment, LibraryFinePayment, FeePayment
# Register your models here.
@admin.register(LibraryFinePayment)
class LibraryFinePaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'fine', 'amount', 'payment_date', 'payment_method', 'payment_reference', 'paid')
    