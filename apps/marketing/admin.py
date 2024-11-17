from django.contrib import admin


from apps.marketing.models import Lead, Campaign


# Register your models here.
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "phone_number",
        "gender",
        "source",
        "status",
        "created_on",
    )


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "campaign_type",
        "start_date",
        "end_date",
        "status",
        "created_on",
    )
