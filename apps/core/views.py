from datetime import datetime, timedelta
import calendar

from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from django.db import transaction

from apps.students.models import Student, MealCard
from apps.staff.models import Staff
from apps.hostels.models import Booking
from apps.core.models import UserRole, Campus, StudyYear

from django.views.generic import ListView
from django.http import JsonResponse


# Create your views here.
@login_required
def home(request):
    students_count = Student.objects.count()
    staff_count = Staff.objects.count()
    meal_cards_count = MealCard.objects.count()
    bookings_count = Booking.objects.count()

    context = {
        "students_count": students_count,
        "staff_count": staff_count,
        "meal_cards_count": meal_cards_count,
        "bookings_count": bookings_count,
    }
    return render(request, "home.html", context)


def campuses(request):
    campuses = Campus.objects.all().order_by("-created_on")

    paginator = Paginator(campuses, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}
    return render(request, "campuses/campuses.html", context)


def new_campus(request):
    if request.method == "POST":
        name = request.POST.get("name")
        city = request.POST.get("city")
        address = request.POST.get("address")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        population = request.POST.get("population")

        Campus.objects.create(
            name=name,
            city=city,
            address=address,
            phone_number=phone_number,
            email=email,
            population=population,
        )

        return redirect("campuses")
    return render(request, "campuses/new_campus.html")


def edit_campus(request):
    if request.method == "POST":
        campus_id = request.POST.get("campus_id")
        name = request.POST.get("name")
        city = request.POST.get("city")
        address = request.POST.get("address")
        phone_number = request.POST.get("phone_number")
        email = request.POST.get("email")
        population = request.POST.get("population")

        Campus.objects.filter(id=campus_id).update(
            name=name,
            city=city,
            address=address,
            phone_number=phone_number,
            email=email,
            population=population,
        )

        return redirect("campuses")
    return render(request, "campuses/edit_campus.html")


def delete_campus(request):
    if request.method == "POST":
        campus_id = request.POST.get("campus_id")
        Campus.objects.get(id=campus_id).delete()
        return redirect("campuses")
    return render(request, "campuses/delete_campus.html")


def study_years(request):
    years = StudyYear.objects.all().order_by("-created_on")

    context = {"years": years}

    return render(request, "admissions/years/years.html", context)


def new_study_year(request):
    if request.method == "POST":
        name = request.POST.get("name")

        StudyYear.objects.create(name=name)
        return redirect("study-years")
    return render(request, "admissions/years/new_year.html")


def edit_study_year(request):
    if request.method == "POST":
        id = request.POST.get("year_id")
        name = request.POST.get("name")

        year = StudyYear.objects.get(id=id)
        year.name = name
        year.save()
        return redirect("study-years")
    return render(request, "admissions/years/edit_year.html")


def delete_study_year(request):
    if request.method == "POST":
        id = request.POST.get("year_id")

        year = StudyYear.objects.get(id=id)
        year.delete()
        return redirect("study-years")
    return render(request, "admissions/years/delete_year.html")
