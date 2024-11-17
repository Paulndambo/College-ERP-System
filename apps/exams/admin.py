from django.contrib import admin

from apps.exams.models import ExamData


# Register your models here.
@admin.register(ExamData)
class ExamDataAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "semester",
        "course",
        "cat_one",
        "cat_two",
        "exam_marks",
        "total_marks",
        "marks_total",
    )
