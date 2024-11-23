from datetime import datetime, timedelta
import calendar
from decimal import Decimal

from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from django.db import transaction

from django.views.generic import ListView
from django.http import JsonResponse

from apps.exams.models import ExamData
from apps.schools.models import Semester, Course
from apps.students.models import Student

students_list = Student.objects.all()
semesters_list = Semester.objects.all()
courses_list = Course.objects.all()
class ExamMarksListView(ListView):
    model = ExamData
    template_name = 'exams/student_marks.html'
    context_object_name = 'students-marks'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) |
                Q(student__registration_number__icontains=search_query) |
                Q(student__user__first_name__icontains=search_query) 
            )
        
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context["students"] = students_list
        context["semesters"] = semesters_list
        context["courses"] = courses_list
        return context


@login_required(login_url="/users/login")
def record_marks(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        course_id = request.POST.get("course_id")
        semester_id = request.POST.get("semester_id")
        cat_one = Decimal(request.POST.get("cat_one"))
        cat_two = Decimal(request.POST.get("cat_two"))
        main_exam = Decimal(request.POST.get("main_exam"))

        marks = ExamData.objects.create(
            student_id=student_id,
            course_id=course_id,
            semester_id=semester_id,
            cat_one=cat_one,
            cat_two=cat_two,
            exam_marks=main_exam,
            recorded_by=request.user,
        )
        marks.total_marks = ((marks.cat_one + marks.cat_two) / 2) + marks.exam_marks
        marks.save()
        messages.success(request, "Marks recorded successfully")
        return redirect("students-marks")
    return render(request, "exams/record_marks.html")


@login_required(login_url="/users/login")
def edit_marks(request):
    if request.method == "POST":
        marks_id = request.POST.get("marks_id")
        course_id = request.POST.get("course_id")
        semester_id = request.POST.get("semester_id")
        cat_one = Decimal(request.POST.get("cat_one"))
        cat_two = Decimal(request.POST.get("cat_two"))
        main_exam = Decimal(request.POST.get("main_exam"))

        marks = ExamData.objects.get(id=marks_id)
        marks.cat_one = cat_one
        marks.cat_two = cat_two
        marks.exam_marks = main_exam
        marks.recorded_by = request.user
        marks.semester_id = semester_id
        marks.course_id = course_id
        marks.save()

        marks.total_marks = ((marks.cat_one + marks.cat_two) / 2) + marks.exam_marks
        marks.save()
        messages.success(request, "Marks updated successfully")
        return redirect("students-marks")
    return render(request, "exams/edit_marks.html")


def delete_marks(request):
    if request.method == "POST":
        marks_id = request.POST.get("marks_id")
        ExamData.objects.get(id=marks_id).delete()
        messages.success(request, "Marks deleted successfully")
        return redirect("students-marks")
    return render(request, "exams/delete_marks.html")
