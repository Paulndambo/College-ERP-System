from datetime import datetime, timedelta
import calendar
from decimal import Decimal

from django.shortcuts import render, redirect
from django.db.models import Q, Avg
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField, Sum
from django.db import transaction

from django.views.generic import ListView
from django.http import JsonResponse

from apps.exams.grading import generate_grade
from apps.exams.models import ExamData
from apps.schools.models import Semester, ProgrammeCohort, Programme
from apps.students.models import Student


def transcripts(request):
    return render(request, "exams/transcripts/home.html")


class StudentsTranscriptsListView(ListView):
    model = Student
    template_name = "exams/transcripts/students/student_transcripts.html"
    context_object_name = "student-transcripts"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(registration_number__icontains=search_query)
                | Q(user__first_name__icontains=search_query)
            )

        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        return context


def student_transcripts_details(request, student_id=None):
    student = Student.objects.get(id=student_id)

    student_marks = list(
        ExamData.objects.filter(student_id=student_id)
        .values_list("semester_id", flat=True)
        .distinct()
    )

    semesters = (
        Semester.objects.filter(id__in=student_marks)
        .annotate(
            average_marks=Avg("semestermarks__total_marks")
        )  # Calculate average marks per semester
        .annotate(
            average_grade=Case(
                When(average_marks__gte=70, then=Value("A")),
                When(average_marks__gte=60, then=Value("B")),
                When(average_marks__gte=50, then=Value("C")),
                When(average_marks__gte=40, then=Value("D")),
                default=Value("F"),
            )
        )
        .order_by("-created_on")
    )

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


def department_transcripts(request, department_id=None):
    return render(request, "exams/transcripts/department_transcripts.html")


class CohortsListView(ListView):
    model = ProgrammeCohort
    template_name = "exams/cohorts/cohorts.html"
    context_object_name = "cohorts"
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(name__icontains=search_query)
                | Q(programme__name__icontains=search_query)
            )
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        return context


class CohortsSemestersListView(ListView):
    model = Semester
    template_name = "exams/cohorts/cohort_semesters.html"
    context_object_name = "semester"
    paginate_by = 8

    cohort = ProgrammeCohort.objects.none()

    def get_queryset(self):
        cohort_id = self.kwargs["cohort_id"]
        self.cohort = ProgrammeCohort.objects.get(id=cohort_id)

        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(name__icontains=search_query)
                | Q(academic_year__icontains=search_query)
            )
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["cohort"] = self.cohort
        return context


def cohort_transcripts_details(request, semester_id=None, cohort_id=None):
    students = (
        Student.objects.prefetch_related("studentmarks")
        .filter(
            studentmarks__semester_id=semester_id, studentmarks__cohort_id=cohort_id
        )
        .annotate(average_marks=Avg("studentmarks__total_marks"))
        .annotate(
            average_grade=Case(
                When(average_marks__gte=70, then=Value("A")),
                When(average_marks__gte=60, then=Value("B")),
                When(average_marks__gte=50, then=Value("C")),
                When(average_marks__gte=40, then=Value("D")),
                default=Value("F"),
            )
        )
    )

    paginator = Paginator(students, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "students": students,
        "semester_id": semester_id,
    }

    return render(request, "exams/cohorts/cohort_transcripts_details.html", context)


class ProgrammesListView(ListView):
    model = Programme
    template_name = "exams/transcripts/programmes/programmes.html"
    context_object_name = "programmes"
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) | Q(name__icontains=search_query)
            )

        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        return context


class ProgrammesSemestersListView(ListView):
    model = Semester
    template_name = "exams/transcripts/programmes/programme_semesters.html"
    context_object_name = "semester"
    paginate_by = 8

    programme = Programme.objects.none()

    def get_queryset(self):
        programme_id = self.kwargs["programme_id"]
        self.programme = Programme.objects.get(id=programme_id)

        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(name__icontains=search_query)
                | Q(academic_year__icontains=search_query)
            )
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["programme"] = self.programme
        return context


def programme_transcripts(request, semester_id=None, programme_id=None):
    students = (
        Student.objects.prefetch_related("studentmarks")
        .filter(
            studentmarks__semester_id=semester_id,
            studentmarks__course__programme_id=programme_id,
        )
        .annotate(average_marks=Avg("studentmarks__total_marks"))
        .annotate(
            average_grade=Case(
                When(average_marks__gte=70, then=Value("A")),
                When(average_marks__gte=60, then=Value("B")),
                When(average_marks__gte=50, then=Value("C")),
                When(average_marks__gte=40, then=Value("D")),
                default=Value("F"),
            )
        )
    )

    paginator = Paginator(students, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "students": students,
        "semester_id": semester_id,
    }

    return render(
        request, "exams/transcripts/programmes/programme_transcripts.html", context
    )
