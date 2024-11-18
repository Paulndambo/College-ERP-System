from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages

from apps.staff.models import Staff, Department
from apps.users.models import User
from apps.core.models import UserRole


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
            position=position
        )
        return redirect("staff")
    return render(request, "staff/new_staff.html")
