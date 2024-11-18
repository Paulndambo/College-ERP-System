from django.shortcuts import render, redirect
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from django.db import transaction

from django.views.generic import ListView
from django.http import JsonResponse

from apps.schools.models import CourseSession, ProgrammeCohort


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
        return context
    
    
def new_cohort(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        programme = request.POST.get('programme')
        current_year = request.POST.get('current_year')
        current_semester = request.POST.get('current_semester')
        
        ProgrammeCohort.objects.create(
            name=name, 
            programme_id=programme,
            current_year=current_year,
            current_semester_id=current_semester
        )
        redirect('cohorts')
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
        redirect('cohorts')
    return render(request, 'cohorts/edit_cohort.html')


def delete_cohort(request):
    if request.method == 'POST':
        id = request.POST.get('cohort_id')
        ProgrammeCohort.objects.filter(id=id).delete()
        redirect('cohorts')
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
        return context
    
    

def new_session(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        course = request.POST.get('course')
        cohort = request.POST.get('cohort')
        start_time = request.POST.get('start_time')
        period = request.POST.get('period')
        
        CourseSession.objects.create(
            name=name, 
            course_id=course,
            cohort_id=cohort,
            start_time=start_time,
            period=period
        )
        redirect('sessions')
    return render(request, 'sessions/new_session.html')


def edit_session(request):
    if request.method == 'POST':
        id = request.POST.get('session_id')
        name = request.POST.get('name')
        course = request.POST.get('course')
        cohort = request.POST.get('cohort')
        start_time = request.POST.get('start_time')
        period = request.POST.get('period')
        status = request.POST.get('status')
        
        CourseSession.objects.filter(id=id).update(
            name=name, 
            course_id=course,
            cohort_id=cohort,
            start_time=start_time,
            period=period,
            status=status
        )
        redirect('sessions')
    return render(request, 'sessions/edit_session.html')


def delete_session(request):
    if request.method == 'POST':
        id = request.POST.get('session_id')
        CourseSession.objects.filter(id=id).delete()
        redirect('sessions')
    return render(request, 'sessions/delete_session.html')