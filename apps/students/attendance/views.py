from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages

from django.views.generic import ListView
from django.http import JsonResponse
from django.db.models import Q


from apps.students.models import StudentAttendance, Student
from apps.schools.models import ProgrammeCohort, Programme, Course, Semester


class AttendanceDashboardListView(ListView):
    model = ProgrammeCohort
    template_name = "attendance/dashboard.html"
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


class CohortAttendanceDetailView(ListView):
    model = Semester
    template_name = "attendance/cohort_details.html"
    context_object_name = "semesters"
    paginate_by = 5

    cohort = ProgrammeCohort.objects.none()

    def get_queryset(self):
        self.cohort = ProgrammeCohort.objects.get(id=self.kwargs["cohort_id"])
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
        context["cohort"] = self.cohort
        return context
