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

from apps.staff.models import Staff, Department, StaffLeaveApplication, StaffLeave
from apps.users.models import User
from apps.core.models import UserRole

from apps.core.constants import LEAVE_TYPES
# Create your views here.
def staff(request):
    staff = Staff.objects.all().order_by("-created_on")

    paginator = Paginator(staff, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    user_roles = UserRole.objects.exclude(name__in=["Student", "Admin"]).all()
    departments = Department.objects.all()

    context = {
        "page_obj": page_obj,
        "user_roles": user_roles,
        "departments": departments,
    }
    return render(request, "staff/staff.html", context)


class StaffListView(ListView):
    model = Staff
    template_name = "staff/staff.html"
    context_object_name = "staffs"
    paginate_by = 9
    
    user_roles = UserRole.objects.exclude(name__in=["Student", "Admin"]).all()
    departments = Department.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(user__first_name__icontains=search_query)
            )

        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["user_roles"] = self.user_roles
        context["departments"] = self.departments
        return context


def staff_details(request, id):
    staff = Staff.objects.get(id=id)
    context = {"staff": staff}
    return render(request, "staff/staff_details.html", context)


def new_staff(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        gender = request.POST.get("gender")
        phone_number = request.POST.get("phone_number")
        address = request.POST.get("address")
        city = request.POST.get("city")
        country = request.POST.get("country")
        department = request.POST.get("department")
        role = request.POST.get("role")
        position = request.POST.get("position")
        state = request.POST.get("state")
        postal_code = request.POST.get("postal_code")

        user_role = UserRole.objects.get(id=role)

        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=email,
            role=user_role,
            phone_number=phone_number,
            address=address,
            postal_code=postal_code,
            city=city,
            state=state,
            country=country,
            gender=gender,
        )

        staff = Staff.objects.create(
            user=user,
            staff_number=phone_number,
            department_id=department,
            position=position,
        )
        return redirect("staff")
    return render(request, "staff/new_staff.html")


class LeaveApplicationListView(ListView):
    model = StaffLeaveApplication
    template_name = "staff/leaves/applications.html"
    context_object_name = "applications"
    paginate_by = 8
    
    staffs = Staff.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(staff__user__first_name__icontains=search_query)
            )
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["staffs"] = self.staffs
        context["leave_types"] = LEAVE_TYPES
        return context


def leave_application_details(request, id):
    application = StaffLeaveApplication.objects.get(id=id)
    context = {"application": application}
    return render(request, "staff/leaves/details.html", context)


def new_leave_application(request):
    if request.method == "POST":
        staff = request.POST.get("staff_id")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        leave_type = request.POST.get("leave_type")
        reason = request.POST.get("reason")

        StaffLeaveApplication.objects.create(
            staff_id=staff,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            leave_type=leave_type,
            status="Pending",
        )
        return redirect("leave-applications")
    return render(request, "staff/leaves/new_application.html")


def edit_leave_application(request):
    if request.method == "POST":
        id = request.POST.get("application_id")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        leave_type = request.POST.get("leave_type")
        reason = request.POST.get("reason")

        application = StaffLeaveApplication.objects.get(id=id)
        application.start_date = start_date
        application.end_date = end_date
        application.reason = reason
        application.leave_type = leave_type
        application.save()
        return redirect("leave-applications")
    return render(request, "staff/leaves/edit_application.html")


def approve_leave_application(request):
    if request.method == "POST":
        id = request.POST.get("application_id")
        application = StaffLeaveApplication.objects.get(id=id)
        application.status = "Approved"
        application.save()
        
        StaffLeave.objects.create(
            application=application
        )
        return redirect("leave-applications")
    return render(request, "staff/leaves/approve_application.html")


def decline_leave_application(request):
    if request.method == "POST":
        id = request.POST.get("application_id")
        decline_reason = request.POST.get("decline_reason")
        application = StaffLeaveApplication.objects.get(id=id)
        application.status = "Declined"
        application.reason_declined = decline_reason
        application.save()
        return redirect("leave-applications")
    return render(request, "staff/leaves/decline_application.html")



class LeavesListView(ListView):
    model = StaffLeave
    template_name = "staff/leaves/leaves.html"
    context_object_name = "leaves"
    paginate_by = 8
    

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(application__staff__user__first_name__icontains=search_query)
            )
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        return context
    

def leave_details(request, id):
    leave = StaffLeave.objects.get(id=id)
    context = {"leave": leave}
    return render(request, "staff/leaves/leave_details.html", context)    
    

def complete_leave(request):
    if request.method == "POST":
        id = request.POST.get("leave_id")
        leave = StaffLeave.objects.get(id=id)
        leave.status = "Completed"
        leave.save()
        return redirect("leaves")
    return render(request, "staff/leaves/complete_leave.html")


def cancel_leave(request):
    if request.method == "POST":
        id = request.POST.get("leave_id")
        reason_cancelled = request.POST.get("reason_cancelled")
        leave = StaffLeave.objects.get(id=id)
        leave.status = "Cancelled"
        leave.reason_cancelled = reason_cancelled
        leave.save()
        return redirect("leaves")
    return render(request, "staff/leaves/cancel_leave.html")