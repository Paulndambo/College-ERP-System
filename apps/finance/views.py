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

from apps.finance.models import LibraryFinePayment, Payment, FeePayment, Budget

date_today = datetime.now().date()


def finance_home(request):
    return render(request, "finance/dashboard.html")


class BudgetsListView(ListView):
    model = Budget
    template_name = "finance/budgets/budgets.html"
    context_object_name = "budgets"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(title__icontains=search_query)
            )
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        return context


class LibraryFinePaymentListView(ListView):
    model = LibraryFinePayment
    template_name = "finance/library_fines.html"
    context_object_name = "fines"
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(member__user__first_name__icontains=search_query)
            )
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        return context


@login_required
@transaction.atomic
def capture_library_fine_payment(request):
    if request.method == "POST":
        fine_id = request.POST.get("fine_id")
        payment_method = request.POST.get("payment_method")
        payment_reference = request.POST.get("payment_reference")

        fine_payment = LibraryFinePayment.objects.get(id=fine_id)

        fine_payment.fine.paid = True
        fine_payment.fine.save()

        Payment.objects.create(
            payer=fine_payment.member.user,
            payment_method=payment_method,
            payment_reference=payment_reference,
            amount=fine_payment.amount,
            description=f"Library fine payment for {fine_payment.fine.borrow_transaction.member.user.first_name} {fine_payment.fine.borrow_transaction.member.user.last_name}",
            direction="Income",
            payment_type="Library Fine Payment",
            recorded_by=request.user,
        )

        fine_payment.payment_method = payment_method
        fine_payment.payment_reference = payment_reference
        fine_payment.paid = True
        fine_payment.payment_date = date_today
        fine_payment.recorded_by = request.user
        fine_payment.save()

        return redirect("library-fines")
    return render(request, "finance/record_library_fine.html")
