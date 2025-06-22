from django.contrib import admin

from apps.schools.models import (
    School,
    Department,
    Course,
    Programme,
    Semester,
    ProgrammeCohort,
    CourseSession,
)

# Register your models here.

admin.site.register(School)
# admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Programme)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "academic_year", "created_on")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "department_type",
        "school",
        "created_on",
    )


filter_fields = ("school", "department")


@admin.register(ProgrammeCohort)
class ProgrammeCohortAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "programme",
        "current_year",
        "current_semester",
        "created_on",
    )
    list_filter = ("programme", "current_year", "current_semester")


@admin.register(CourseSession)
class CourseSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "cohort", "course", "start_time", "period", "created_on")
    list_filter = ("course", "cohort")
