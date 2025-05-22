from django.contrib import admin

from apps.admissions.models import (
    StudentApplication,
    ApplicationDocument,
    Intake,
    ApplicationEducationHistory,
)


# Register your models here.
@admin.register(StudentApplication)
class StudentApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "slug",
        "first_name",
        "last_name",
        "phone_number",
        "gender",
        "status",
        "intake"
    ]


@admin.register(Intake)
class IntakeAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "start_date", "end_date", "closed"]


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "student_application",
        "document_name",
        "document_type",
        "document_file",
        "verified",
    ]


@admin.register(ApplicationEducationHistory)
class ApplicationEducationHistoryAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "student_application",
        "institution",
        "level",
        "major",
        "year",
        "grade_or_gpa",
        "graduated"
    ]
