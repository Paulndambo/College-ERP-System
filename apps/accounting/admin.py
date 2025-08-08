from django.contrib import admin

from apps.accounting.models import Account, AccountType


# Register your models here.
@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "normal_balance")
    search_fields = ("name",)
    list_filter = ("is_archived",)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "account_code",
        "name",
        "account_type",
        "cash_flow_section",
        "normal_balance",
    )
    search_fields = ("account_code", "name")
    list_filter = (
        "account_type",
        "cash_flow_section",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("account_type")
