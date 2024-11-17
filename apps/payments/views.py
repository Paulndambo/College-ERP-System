from datetime import datetime, timedelta
import calendar

from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction


from apps.payments.models import MealCardPayment, RentPayment
from apps.students.models import Student, MealCard

# Create your views here.
date_today = datetime.now().date()
month_name = calendar.month_name[date_today.month]

months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def rent_payments(request):
    rent_payments = RentPayment.objects.all().order_by("-created_on")

    paginator = Paginator(rent_payments, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj, "months": months}
    return render(request, "payments/rent/rent_payments.html", context)


def new_rent_payment(request):
    if request.method == "POST":
        reg_number = request.POST.get("reg_number")
        amount = request.POST.get("amount")
        month = request.POST.get("month")

        student = Student.objects.get(registration_number=reg_number)

        RentPayment.objects.create(
            student=student,
            amount=amount,
            month=month if month else month_name,
            year=date_today.year,
            payment_date=date_today,
        )
        messages.success(request, "Payment recorded successfully.")
        return redirect("rent-payments")
    return render(request, "payments/rent/new_rent_payment.html")


def mealcard_payments(request):
    meal_card_payments = MealCardPayment.objects.all().order_by("-created_on")

    paginator = Paginator(meal_card_payments, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj, "months": months}
    return render(request, "payments/mealcards/mealcard_payments.html", context)


@transaction.atomic
def new_mealcard_payment(request):
    if request.method == "POST":
        reg_number = request.POST.get("reg_number")
        transaction_code = request.POST.get("transaction_code")
        card_number = request.POST.get("card_number")
        amount = request.POST.get("amount")
        month = request.POST.get("month")

        student = Student.objects.get(registration_number=reg_number)

        meal_card = MealCard.objects.create(
            student=student,
            card_number=card_number,
            expiry_date=date_today + timedelta(days=30),
        )

        MealCardPayment.objects.create(
            student=student,
            mealcard=meal_card,
            transaction_code=transaction_code,
            card_number=card_number,
            amount=amount,
            month=month if month else month_name,
            year=date_today.year,
            payment_date=date_today,
        )

        messages.success(request, "Payment recorded successfully.")
        return redirect("meal-card-payments")
    return render(request, "payments/mealcards/new_meal_card_payment.html")
