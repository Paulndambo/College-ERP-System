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

from apps.visitors.models import Visitor


# Create your views here.
class VisitorListView(ListView):
    model = Visitor
    template_name = "visitors/visitors.html"
    context_object_name = "visitors"
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(name__icontains=search_query)
                | Q(id_number__icontains=search_query)
            )
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        return context


@login_required
def new_visitor(request):
    if request.method == "POST":
        name = request.POST.get("name")
        id_number = request.POST.get("id_number")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        purpose = request.POST.get("purpose")
        gender = request.POST.get("gender")

        Visitor.objects.create(
            name=name,
            id_number=id_number,
            email=email,
            phone=phone,
            purpose=purpose,
            gender=gender,
            recorded_by=request.user,
        )
        return redirect("visitors")
    return render(request, "visitors/new_visitor.html")


@login_required
def edit_visitor(request):
    if request.method == "POST":
        visitor_id = request.POST.get("visitor_id")
        visitor = Visitor.objects.get(id=visitor_id)
        visitor.name = request.POST.get("name")
        visitor.id_number = request.POST.get("id_number")
        visitor.email = request.POST.get("email")
        visitor.phone = request.POST.get("phone")
        visitor.purpose = request.POST.get("purpose")
        visitor.save()
        return redirect("visitors")
    return render(request, "visitors/edit_visitor.html")


@login_required
def checkout_visitor(request, id):
    visitor = Visitor.objects.get(id=id)
    visitor.checkout_time = datetime.now()
    visitor.save()
    return redirect("visitors")


@login_required
def delete_visitor(request):
    if request.method == "POST":
        visitor_id = request.POST.get("visitor_id")
        Visitor.objects.get(id=visitor_id).delete()
        return redirect("visitors")
    return render(request, "visitors/delete_visitor.html")
