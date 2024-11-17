from django.contrib import admin

from apps.schools.models import School, Department, Course, Programme, Semester

# Register your models here.

admin.site.register(School)
admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Programme)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "academic_year", "created_on")
