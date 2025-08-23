from django.contrib import admin

from apps.students.models import (
    SemesterReporting,
    Student,
    StudentDocument,
    StudentAttendance,
    MealCard,
)


# Register your models here.
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "registration_number",
        "status",
        "cohort",
        "hostel_room",
    )
    list_filter = ("status", "hostel_room")
    search_fields = ("registration_number",)


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "document_type", "document_name", "document_file")
    list_filter = ("student",)


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ["id", "student", "session", "status", "date"]


@admin.register(SemesterReporting)
class SemesterReportingAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "student",
        "cohort",
        "semester",
        "academic_year",
        "reported",
        "created_on",
        "updated_on",
    ]
    list_filter = ["cohort", "semester", "reported"]
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "academic_year",
    ]
