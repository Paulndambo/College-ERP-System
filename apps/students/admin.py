from django.contrib import admin

from apps.students.models import Student, StudentDocument


# Register your models here.
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "registration_number", "status")
    list_filter = ("status",)


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "name", "file")
    list_filter = ("student",)
