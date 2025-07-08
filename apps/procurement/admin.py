from django.contrib import admin

from apps.procurement.models import Tender, TenderApplication, TenderAward, Vendor

@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ("title", "deadline", "created_by", "status", "projected_amount", "actual_amount")
    search_fields = ("title", "description")
    list_filter = ("created_by", "deadline", "status")


@admin.register(TenderApplication)
class TenderApplicationAdmin(admin.ModelAdmin):
    list_display = ("company_name", "tender", "status")
    search_fields = ("company_name", "tender__title")
    list_filter = ("status", "tender__created_by")
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "address")
    search_fields = ("name", "email", "phone", "address")
    list_filter = ("name", "email", "phone", "address")
    
@admin.register(TenderAward)
class TenderAwardAdmin(admin.ModelAdmin):
    list_display = ("tender", "vendor", "award_amount")
    search_fields = ("tender__title", "vendor__name")
    list_filter = ("tender__created_by", "vendor__name")
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("tender", "vendor")