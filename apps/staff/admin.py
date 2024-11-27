from django.contrib import admin

from apps.staff.models import Staff, Department, StaffLeave, StaffLeaveApplication


# Register your models here.
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "staff_number", "department")
    list_filter = ("department",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_on")
    list_filter = ("name",)


@admin.register(StaffLeaveApplication)
class StaffLeaveApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "staff",
        "leave_type",
        "start_date",
        "end_date",
        "status",
        "created_on",
    )
 

@admin.register(StaffLeave)
class StaffLeaveAdmin(admin.ModelAdmin):
    list_display = ("id", "application", "status", "created_on")
   