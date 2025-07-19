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

from apps.finance.models import FeeStructure, FeeStructureItem
from apps.schools.models import Programme, Semester
from apps.core.models import StudyYear


class FeesStructuresProgrammesListView(ListView):
    model = Programme
    template_name = "finance/fees_structures/programmes.html"
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


class FeeStructureListView(ListView):
    model = FeeStructure
    template_name = "finance/fees_structures/fees_structures.html"
    context_object_name = "fees_structures"
    paginate_by = 8

    programme = Programme.objects.none()
    semesters = Semester.objects.all()
    years_of_study = StudyYear.objects.all()

    def get_queryset(self):
        programme_id = self.kwargs.get("programme_id")
        queryset = super().get_queryset().filter(programme_id=programme_id)
        search_query = self.request.GET.get("search", "")

        self.programme = Programme.objects.get(id=programme_id)

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(semester__name__icontains=search_query)
                | Q(year_of_study__name__icontains=search_query)
            )
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["programme"] = self.programme
        context["semesters"] = self.semesters
        context["years_of_study"] = self.years_of_study
        return context


def fees_structire_details(request, id):
    structure = FeeStructure.objects.get(id=id)
    items = FeeStructureItem.objects.filter(fee_structure=structure)

    context = {"structure": structure, "items": items}
    return render(
        request, "finance/fees_structures/fee_structure_details.html", context
    )


def new_fees_structure(request):
    if request.method == "POST":
        programme_id = request.POST.get("programme_id")
        semester_id = request.POST.get("semester_id")
        year_id = request.POST.get("year_id")

        FeeStructure.objects.create(
            programme_id=programme_id, semester_id=semester_id, year_of_study_id=year_id
        )
        return redirect("fees-structures", programme_id=programme_id)
    return render(request, "finance/fees_structures/new_fee_structure.html")


def edit_fees_structure(request):
    if request.method == "POST":
        fee_structure_id = request.POST.get("fee_structure_id")
        year_id = request.POST.get("year_id")
        semester_id = request.POST.get("semester_id")

        structure = FeeStructure.objects.get(id=fee_structure_id)
        structure.year_of_study_id = year_id
        structure.semester_id = semester_id
        structure.save()
        return redirect("fees-structures", programme_id=structure.programme.id)
    return render(request, "finance/fees_structures/edit_fee_structure.html")


def delete_fees_structure(request):
    if request.method == "POST":
        fee_structure_id = request.POST.get("fee_structure_id")
        structure = FeeStructure.objects.get(id=fee_structure_id)
        structure.delete()
        return redirect("fees-structures", programme_id=structure.programme.id)
    return render(request, "finance/fees_structures/delete_fee_structure.html")
