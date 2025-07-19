from django.contrib import admin

from apps.accounting.models import Account, AccountType

# Register your models here.
@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "normal_balance")
    search_fields = ("name",)
    
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("account_code", "name", "account_type")
    search_fields = ("account_code", "name")
    list_filter = ("account_type",)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("account_type")