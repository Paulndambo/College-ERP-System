from django.contrib import admin

from apps.core.models import RolePermission, UserRole, Module


# Register your models here.
@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_on")


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_on", "updated_on", "code")


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("id", "role", "module", "can_view", "created_on", "updated_on")
