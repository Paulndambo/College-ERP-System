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

from apps.admissions.models import StudentApplication, ApplicationDocument, ApplicationEducationHistory, Intake
from apps.schools.models import Programme

date_today = datetime.now().date()
# Create your views here.
class StudentApplicationsListView(ListView):
    model = StudentApplication
    template_name = 'admissions/applications.html'
    context_object_name = 'applications'
    paginate_by = 8
    
    programmes = Programme.objects.all()
    intakes = Intake.objects.all()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) |
                Q(id_number__icontains=search_query),
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )
        
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context["programmes"] = self.programmes
        context["intakes"] = self.intakes
        return context
    

def application_details(request, id):
    application = StudentApplication.objects.get(id=id)
    
    documents = ApplicationDocument.objects.filter(student_application=application)
    education_history = ApplicationEducationHistory.objects.filter(student_application=application)
    
    gender_choices = ["Male", "Female"]
    GUARDIAN_RELATIONSHIPS = ["Parent", "Grand Parent", "Sibling", "Aunt/Uncle", "Other"]
    
    context = {
        "application": application,
        "documents": documents,
        "education_history": education_history,
        "gender_choices": gender_choices,
        "relationship_choices":  GUARDIAN_RELATIONSHIPS 
    }
    return render(request, "admissions/application_details.html", context)


def edit_application(request):
    if request.method == "POST":
        application_id = request.POST.get("application_id")
        
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        id_number = request.POST.get("id_number")
        passport_number = request.POST.get("passport_number")
        date_of_birth = request.POST.get("date_of_birth")
        gender = request.POST.get("gender")
        
        
        guardian_name = request.POST.get("guardian_name")
        guardian_email = request.POST.get("guardian_email")
        guardian_relationship = request.POST.get("guardian_relationship")
        guardian_phone_number = request.POST.get("guardian_phone_number")
        
        address = request.POST.get("address")
        postal_code = request.POST.get("postal_code")
        city = request.POST.get("city")
        country = request.POST.get("country")
        
        intake_id = request.POST.get("intake_id")
        first_choice_programme_id = request.POST.get("first_choice_programme_id")
        second_choice_programme_id = request.POST.get("second_choice_programme_id")
        
        a = StudentApplication.objects.get(id=application_id)
        
        a.first_name = first_name if first_name else a.first_name
        a.last_name = last_name if last_name else a.last_name
        a.email = email if email else a.email
        a.phone_number = phone_number if phone_number else a.phone_number
        a.id_number = id_number if id_number else a.id_number
        a.passport_number = passport_number if passport_number else a.passport_number
        a.date_of_birth = date_of_birth if date_of_birth else a.date_of_birth
        a.gender = gender if gender else a.gender
        
        a.guardian_name = guardian_name if guardian_name else a.guardian_name
        a.guardian_email = guardian_email if guardian_email else a.guardian_email
        a.guardian_relationship = guardian_relationship if guardian_relationship else a.guardian_relationship
        a.guardian_phone_number = guardian_phone_number if guardian_phone_number else a.guardian_phone_number
        
        a.address = address if address else a.address
        a.postal_code = postal_code if postal_code else a.postal_code
        a.city = city if city else a.city
        a.country = country if country else a.country
        
        a.intake_id = intake_id if intake_id else a.intake_id
        a.first_choice_programme_id = first_choice_programme_id if first_choice_programme_id else a.first_choice_programme_id
        a.second_choice_programme_id = second_choice_programme_id if second_choice_programme_id else a.second_choice_programme_id
        
        a.save()
        return redirect("application-details", id=application_id)
    

def verify_document(request, document_id):
    document = ApplicationDocument.objects.get(id=document_id)
    document.verified = True
    document.save()
    return redirect("application-details", id=document.student_application.id)


def start_student_application(request):
    if request.method == "POST":
        application = StudentApplication.objects.create(
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            email=request.POST.get("email"),
            phone_number=request.POST.get("phone_number"),
            id_number=request.POST.get("id_number"),
            first_choice_programme_id=request.POST.get("programme_id"),
            intake_id=request.POST.get("intake_id"),
            status="Draft",
            gender=request.POST.get("gender")
        )
        application.application_number = f"APP-{application.id}/{date_today.month}/{date_today.year}"
        application.save()
        return redirect("applications")
    return render(request, "admissions/start_application.html")

def apply_for_college(request):
    return render(request, "admissions/apply_for_college.html")