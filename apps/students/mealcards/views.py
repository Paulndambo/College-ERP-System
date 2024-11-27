from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages

from django.views.generic import ListView
from django.http import JsonResponse
from django.db.models import Q

from apps.students.models import Student, MealCard
from apps.core.constants import MONTHS_LIST


class MealCardsListView(ListView):
    model = MealCard
    template_name = "mealcards/mealcards.html"
    context_object_name = "mealcards"
    paginate_by = 9

    students = Student.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(card_number__icontains=search_query)
                | Q(student__registration_number__icontains=search_query)
            )

        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["students"] = self.students
        context["months"] = MONTHS_LIST
        return context


def new_meal_card(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        card_number = request.POST.get("card_number")
        month = request.POST.get("month")
        expiry_date = request.POST.get("expiry_date")

        student = Student.objects.get(id=student_id)
        MealCard.objects.create(
            student=student,
            card_number=card_number,
            month=month,
            expiry_date=expiry_date,
        )
        return redirect("meal-cards")
    return render(request, "mealcards/new_mealcard.html", {"months": MONTHS_LIST})
