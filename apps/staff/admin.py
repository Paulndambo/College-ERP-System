from django.contrib import admin

from apps.staff.models import (
    Staff,
    StaffDocuments,
    StaffLeave,
    StaffLeaveEntitlement,
    StaffPosition,
    StaffLeaveApplication,
    StaffPayroll,
    Payslip,
    StaffOnboardingProgress,
)


@admin.register(StaffPosition)
class StaffPositionAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_filter = ("name",)

@admin.register(StaffLeaveEntitlement)
class StaffLeaveEntitlementAdmin(admin.ModelAdmin):
    list_display = ("id", "staff", "total_days", "used_days", "year")
    list_filter = ("staff", "year")

@admin.register(StaffDocuments)
class StaffDocumentsAdmin(admin.ModelAdmin):
    list_display = ("id", "staff", "document_type", "document_file", "notes")


@admin.register(StaffOnboardingProgress)
class StaffOnboardingProgressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "staff",
        "documents_uploaded",
        "payroll_setup_completed",
        "staff_details_completed",
        "onboarding_completed",
        "user_created",
    )
    list_filter = (
        "staff",
        "documents_uploaded",
        "payroll_setup_completed",
        "staff_details_completed",
        "onboarding_completed",
        "user_created",
    )


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "staff_number",
        "department",
        "position",
        "status",
        "onboarding_status",
    )
    list_filter = ("department", "status", "onboarding_status")


@admin.register(StaffPayroll)
class StaffPayrollAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "staff",
        "basic_salary",
        "house_allowance",
        "transport_allowance",
        "other_allowances",
        "nssf_number",
        "nhif_number",
        "kra_pin",
        "bank_name",
        "bank_account_number",
        "mpesa_number",
        "payment_frequency",
        "created_on",
        "updated_on",
    )
    list_filter = (
        "bank_name",
        "basic_salary",
    )


@admin.register(Payslip)
class PaySlipAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "staff",
        "payroll_period_start",
        "payroll_period_end",
        "basic_salary",
        "total_allowances",
        "total_deductions",
        "total_overtime",
    )


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
