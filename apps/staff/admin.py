from django.contrib import admin

from apps.staff.models import Staff, Department


# Register your models here.
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "staff_number", "department")
    list_filter = ("department",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_on")
    list_filter = ("name",)
