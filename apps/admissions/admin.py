from django.contrib import admin

from apps.admissions.models import StudentApplication, ApplicationDocument
# Register your models here.
@admin.register(StudentApplication)
class StudentApplicationAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "last_name", "phone_number", "gender", "status"]
