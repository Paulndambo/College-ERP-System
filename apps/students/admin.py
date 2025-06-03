from django.contrib import admin

from apps.students.models import Student, StudentDocument, StudentAttendance


# Register your models here.
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "registration_number", "status", "cohort", "hostel_room")
    list_filter = ("status", "hostel_room")
    search_fields = ("registration_number",)


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "document_type", "document_name", "document_file")
    list_filter = ("student",)


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ["id", "student", "session", "status", "date"]
