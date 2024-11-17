from django.contrib import admin

from apps.core.models import UserRole


# Register your models here.
@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_on")
