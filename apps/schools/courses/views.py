from datetime import datetime

from django.shortcuts import render, redirect
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from django.db import transaction

from django.views.generic import ListView
from django.http import JsonResponse

from apps.students.models import StudentAttendance, Student
from apps.schools.models import CourseSession, ProgrammeCohort, Semester, Programme, Course


from apps.core.constants import ACADEMIC_YEARS, SESSION_STATUSES

semesters = Semester.objects.all()
programmes = Programme.objects.all()
courses = Course.objects.all()
cohorts_list = ProgrammeCohort.objects.all()

class CohortsListView(ListView):
    model = ProgrammeCohort
    template_name = 'cohorts/cohorts.html'
    context_object_name = 'cohorts'
    paginate_by = 8
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(programme__name__icontains=search_query)
            )
        
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context["programmes"] = programmes
        context["semesters"] = semesters
        context["cohort_years"] = ACADEMIC_YEARS
        return context
    
    
def new_cohort(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        programme = request.POST.get('programme')
        current_year = request.POST.get('current_year')
        current_semester = request.POST.get('current_semester')
        status = request.POST.get('status')
        
        ProgrammeCohort.objects.create(
            name=name, 
            programme_id=programme,
            current_year=current_year,
            current_semester_id=current_semester,
            status=status
        )
        return redirect('cohorts')
    return render(request, 'cohorts/new_cohort.html')


def edit_cohort(request):
    if request.method == 'POST':
        id = request.POST.get('cohort_id')
        name = request.POST.get('name')
        programme = request.POST.get('programme')
        current_year = request.POST.get('current_year')
        current_semester = request.POST.get('current_semester')
        status = request.POST.get('status')
        
        ProgrammeCohort.objects.filter(id=id).update(
            name=name, 
            programme_id=programme,
            current_year=current_year,
            current_semester_id=current_semester,
            status=status
        )
        return redirect('cohorts')
    return render(request, 'cohorts/edit_cohort.html')


def delete_cohort(request):
    if request.method == 'POST':
        id = request.POST.get('cohort_id')
        ProgrammeCohort.objects.filter(id=id).delete()
        return redirect('cohorts')
    return render(request, 'cohorts/delete_cohort.html')


class CourseSessionsListView(ListView):
    model = CourseSession
    template_name = 'sessions/sessions.html'
    context_object_name = 'sessions'
    paginate_by = 8
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) |
                Q(course__name__icontains=search_query) |
                Q(cohort__name__icontains=search_query)
            )
        
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context["cohorts"] = cohorts_list
        context["courses"] = courses
        context["session_statuses"] = SESSION_STATUSES
        return context
    
    
@transaction.atomic
def new_session(request):
    if request.method == 'POST':
        course = request.POST.get('course')
        cohort = request.POST.get('cohort')
        start_time = request.POST.get('start_time')
        period = request.POST.get('period')
        status = request.POST.get('status')
        
        session = CourseSession.objects.create(
            course_id=course,
            cohort_id=cohort,
            start_time=start_time,
            period=period,
            status=status
        )
        
        students = Student.objects.filter(cohort=session.cohort)
        attendance_list = []
        
        for student in students:
            format_str = "%Y-%m-%dT%H:%M"
            formatted_date = datetime.strptime(session.start_time, format_str).date()
            
            attendance_list.append(
                StudentAttendance(
                    student=student,
                    session=session,
                    date=formatted_date
                )
            )
            
        StudentAttendance.objects.bulk_create(attendance_list)
        
        
        return redirect('sessions')
    return render(request, 'sessions/new_session.html')


def session_attendance(request, id):
    session = CourseSession.objects.get(id=id)
    
    attendees = session.sessionattendances.all()
    paginator = Paginator(attendees, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "page_obj": page_obj
    }
    return render(request, "sessions/session_attendance.html", context)


class CourseSessionAttendancesListView(ListView):
    model = StudentAttendance
    template_name = 'sessions/session_attendance.html'
    context_object_name = 'attendances'
    paginate_by = 6
    
    cohort_session = CourseSession.objects.none()

    def get_queryset(self):
        session_id = self.kwargs['id']  # Access the 'id' parameter from the URL
        queryset = super().get_queryset().filter(session_id=session_id)
        search_query = self.request.GET.get('search', '')
        
        self.cohort_session = CourseSession.objects.get(id=session_id)
        
        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) |
                Q(student__registration_number__icontains=search_query) |
                Q(student__user__first_name__icontains=search_query)
            )
        
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')  # Pass the search query back to the template
        context["cohort_session"] = self.cohort_session
        return context


def mark_student_absent(request):
    if request.method == "POST":
        attendance_id = request.POST.get("attendance_id")
        attendance = StudentAttendance.objects.get(id=attendance_id)
        attendance.status = "Absent"
        attendance.save()
        
        page_number = request.GET.get("page")
        print(f"Current Page: {page_number}")
        
        return redirect(f'/schools/sessions/{attendance.session.id}/attendances/?page={page_number}')
        #return redirect(f"/schools/sessions/{attendance.session.id}/attendances")
    return render(request, "sessions/mark_student_absent.html")


def mark_student_present(request):
    if request.method == "POST":
        attendance_id = request.POST.get("attendance_id")
        attendance = StudentAttendance.objects.get(id=attendance_id)
        attendance.status = "Present"
        attendance.save()
        
        page_number = request.GET.get("page")
        print(f"Current Page: {page_number}")
        
        return redirect(f'/schools/sessions/{attendance.session.id}/attendances/?page={page_number}')
        #return redirect(f"/schools/sessions/{attendance.session.id}/attendances")
    return render(request, "sessions/mark_student_present.html")

def edit_session(request):
    if request.method == 'POST':
        id = request.POST.get('session_id')
        course = request.POST.get('course')
        cohort = request.POST.get('cohort')
        start_time = request.POST.get('start_time')
        period = request.POST.get('period')
        status = request.POST.get('status')
        
        CourseSession.objects.filter(id=id).update(
            course_id=course,
            cohort_id=cohort,
            start_time=start_time,
            period=period,
            status=status
        )
        return redirect('sessions')
    return render(request, 'sessions/edit_session.html')


def delete_session(request):
    if request.method == 'POST':
        id = request.POST.get('session_id')
        session = CourseSession.objects.filter(id=id)
        session.delete()
        return redirect('sessions')
    return render(request, 'sessions/delete_session.html')