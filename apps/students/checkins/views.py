from datetime import datetime
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages

from django.views.generic import ListView
from django.http import JsonResponse
from django.db.models import Q

from apps.students.models import Student, StudentCheckIn


class StudentCheckInListView(ListView):
    model = StudentCheckIn
    template_name = "students/checkins/checkins.html"
    context_object_name = "checkins"
    paginate_by = 9

    students = Student.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(student__registration_number__icontains=search_query)
            )

        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["students"] = self.students
        return context


@login_required
def checkin_student(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        StudentCheckIn.objects.create(student_id=student_id, recorded_by=request.user)
        return redirect("student-checkins")
    return render(request, "students/checkins/checkin_student.html")


@login_required
def checkout_student(request, id=None):
    checkin = StudentCheckIn.objects.get(id=id)
    checkin.check_out_time = datetime.now()
    checkin.save()
    return redirect("student-checkins")
    return render(request, "students/checkins/checkout_student.html")


@login_required
def delete_checkin_record(request):
    if request.method == "POST":
        checkin_id = request.POST.get("checkin_id")
        checkin = StudentCheckIn.objects.get(id=checkin_id)
        checkin.delete()
        return redirect("student-checkins")
    return render(request, "students/checkins/delete_checkin.html")
