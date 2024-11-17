from datetime import datetime, timedelta
import calendar
from decimal import Decimal

from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField, Sum
from django.db import transaction


from apps.exams.models import ExamData
from apps.schools.models import Semester
from apps.students.models import Student


def transcripts(request):
    return render(request, "exams/transcripts/home.html")


def student_transcripts(request):
    students = Student.objects.all().order_by("-created_on")

    paginator = Paginator(students, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    print(students)

    context = {"page_obj": page_obj}
    return render(
        request, "exams/transcripts/students/student_transcripts.html", context
    )


def student_transcripts_details(request, student_id=None):
    student = Student.objects.get(id=student_id)

    student_marks = list(
        ExamData.objects.filter(student_id=student_id)
        .values_list("semester_id", flat=True)
        .distinct()
    )

    print(student_marks)

    semesters = Semester.objects.filter(id__in=student_marks).order_by("-created_on")

    context = {"semesters": semesters, "student_id": student_id, "student": student}

    return render(request, "exams/transcripts/students/transcript.html", context)


def semester_transcripts(request):
    semesters = Semester.objects.all().order_by("-created_on")

    paginator = Paginator(semesters, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}

    return render(
        request, "exams/transcripts/semester/semester_transcripts.html", context
    )


def semester_transcripts_details(request, semester_id=None):
    students = Student.objects.prefetch_related("studentmarks").filter(
        studentmarks__semester_id=semester_id
    )

    paginator = Paginator(students, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "students": students,
        "semester_id": semester_id,
    }

    return render(
        request, "exams/transcripts/semester/semester_transcripts_details.html", context
    )


def department_transcripts(request):
    return render(request, "exams/transcripts/department_transcripts.html")
