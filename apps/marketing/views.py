from datetime import datetime, timedelta
import calendar

from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from django.db import transaction


from apps.marketing.models import Lead, Interaction, Task, LeadStage
from apps.schools.models import Department, Programme, Course
from apps.users.models import User
from apps.core.models import UserRole
from apps.admissions.models import StudentApplication, Intake

from django.views.generic import ListView
from django.http import JsonResponse

from apps.core.constants import GENDER_CHOICES, SOURCES, INTERACTION_TYPES, LEAD_STAGES

programmes = Programme.objects.all()
users_role = UserRole.objects.get(name="Student")
users = User.objects.exclude(role=users_role)


date_today = datetime.now().date()
class LeadsListView(ListView):
    model = Lead
    template_name = 'marketing/leads/leads.html'
    context_object_name = 'leads'
    paginate_by = 8
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(first_name__icontains=search_query) | 
                Q(email__icontains=search_query)
            )
        
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context["users"] = users
        context["sources"] = SOURCES
        context["gender_choices"] = GENDER_CHOICES
        context["programmes"] = programmes
        return context
    
@login_required
def lead_details(request, lead_id):
    lead = Lead.objects.get(id=lead_id)

    interactions = Interaction.objects.filter(lead=lead).order_by("created_on")
    users_role = UserRole.objects.get(name="Student")
    users = User.objects.exclude(role=users_role)
    tasks = Task.objects.filter(lead=lead).order_by("-created_on")

    lead_stages = LeadStage.objects.filter(lead=lead).order_by("-created_on")
    intakes = Intake.objects.all()

    print(users)

    context = {
        "lead": lead,
        "interaction_types": INTERACTION_TYPES,
        "interactions": interactions,
        "users": users,
        "tasks": tasks,
        "stages": LEAD_STAGES,
        "lead_stages": lead_stages,
        "intakes": intakes
    }
    return render(request, "marketing/leads/lead_details.html", context)


@login_required
def capture_lead(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone")
        gender = request.POST.get("gender")
        source = request.POST.get("source")
        programme = request.POST.get("programme")
        city = request.POST.get("city")
        country = request.POST.get("country")

        lead = Lead.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            gender=gender,
            source=source,
            programme_id=programme,
            city=city,
            country=country,
        )

        LeadStage.objects.create(
            lead=lead, stage="New", added_by=request.user
        )

        return redirect("leads")

    return render(request, "marketing/leads/capture_lead.html")


@login_required
def edit_lead(request):
    if request.method == "POST":
        lead_id = request.POST.get("lead_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone")
        gender = request.POST.get("gender")
        source = request.POST.get("source")
        programme = request.POST.get("programme")
        city = request.POST.get("city")
        country = request.POST.get("country")
        assigned_to = request.POST.get("assigned_to")

        lead = Lead.objects.get(id=lead_id)
        lead.first_name = first_name
        lead.last_name = last_name
        lead.email = email
        lead.phone_number = phone_number
        lead.gender = gender
        lead.source = source
        lead.programme_id = programme
        lead.assigned_to_id = assigned_to
        lead.city = city
        lead.country = country
        lead.save()

        return redirect("leads")
    return render(request, "marketing/leads/edit_lead.html")


@login_required
def new_lead_interaction(request):
    if request.method == "POST":
        lead_id = request.POST.get("lead_id")
        interaction_type = request.POST.get("interaction_type")
        notes = request.POST.get("notes")

        Interaction.objects.create(
            interaction_type=interaction_type,
            notes=notes,
            lead_id=lead_id,
            added_by=request.user,
        )
        return redirect("lead-details", lead_id=lead_id)
    return render(request, "marketing/leads/new_lead_interaction.html")


@login_required
def add_lead_stage(request):
    if request.method == "POST":
        lead_id = request.POST.get("lead_id")
        stage = request.POST.get("stage")

        lead_stage = LeadStage.objects.create(
            lead_id=lead_id, added_by=request.user, stage=stage
        )
        lead_stage.lead.status = lead_stage.stage
        lead_stage.lead.save()
        return redirect("lead-details", lead_id=lead_id)
    return render(request, "marketing/leads/new_lead_stage.html")


class TasksListView(ListView):
    model = Task
    template_name = 'marketing/leads/tasks/tasks.html'
    context_object_name = 'tasks'
    paginate_by = 8
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) |
                Q(title__icontains=search_query) 
            )

        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context
    


@login_required
def add_lead_task(request):
    if request.method == "POST":
        lead_id = request.POST.get("lead_id")
        title = request.POST.get("title")
        description = request.POST.get("description")
        due_date = request.POST.get("due_date")

        Task.objects.create(
            lead_id=lead_id,
            user=request.user,
            title=title,
            description=description,
            due_date=due_date,
        )

        return redirect("lead-details", lead_id=lead_id)
    return render(request, "marketing/leads/new_lead_task.html")


@login_required
def mark_task_as_complete(request):
    if request.method == "POST":
        task_id = request.POST.get("task_id")
        task = Task.objects.get(id=task_id)
        task.completed = True
        task.save()
        return redirect("lead-details", lead_id=task.lead.id)
    return render(request, "marketing/leads/mark_as_complete.html")


@login_required
def delete_lead_task(request):
    if request.method == "POST":
        task_id = request.POST.get("task_id")
        task = Task.objects.get(id=task_id)
        task.delete()
        return redirect("lead-details", lead_id=task.lead.id)
    return render(request, "marketing/leads/delete_task.html")


def create_application_with_lead(request):
    if request.method == "POST":
        lead_id = request.POST.get("lead_id")
        id_number = request.POST.get("id_number")
        
        lead = Lead.objects.get(id=lead_id)
        application = StudentApplication.objects.create(
            first_name=lead.first_name,
            last_name=lead.last_name,
            id_number=id_number,
            gender=lead.gender,
            email=lead.email,
            first_choice_programme=lead.programme,
            city=lead.city,
            country=lead.country,
            phone_number=lead.phone_number,
            status="Draft"
        )
        application.application_number = f"APP-{application.id}/{date_today.month}/{date_today.year}"
        application.save()
        lead.status = "Application in Progress"
        lead.save()
        return redirect("lead-details", lead_id=lead.id)
    return render(request, "marketing/leads/start_application.html")