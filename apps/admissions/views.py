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

from apps.core.models import UserRole
from apps.admissions.models import StudentApplication, ApplicationDocument, ApplicationEducationHistory, Intake
from apps.schools.models import Programme, ProgrammeCohort
from apps.users.models import User
from apps.students.models import Student, StudentDocument, StudentEducationHistory

date_today = datetime.now().date()
education_levels = ["Primary School", "Secondary School", "Undergraduate", "Graduate"]
DOCUMENT_TYPES = ["Transcript", "Certificate", "Identification"]
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
    programmes = Programme.objects.all()
    intakes = Intake.objects.all()
    
    cohorts = ProgrammeCohort.objects.filter(programme=application.first_choice_programme).order_by("-created_on")
    print(cohorts)
    
    context = {
        "application": application,
        "documents": documents,
        "education_history": education_history,
        "gender_choices": gender_choices,
        "relationship_choices":  GUARDIAN_RELATIONSHIPS,
        "education_levels": education_levels,
        "document_types": DOCUMENT_TYPES,
        "programmes": programmes,
        "intakes": intakes,
        "cohorts": cohorts
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
    

def upload_application_document(request):
    if request.method == "POST":
        application_id = request.POST.get("application_id")
        document_type = request.POST.get("document_type")
        document_name = request.POST.get("document_name")
        document_file = request.FILES.get("document_file")
        
        ApplicationDocument.objects.create(
            student_application_id=application_id,
            document_type=document_type,
            document_name=document_name,
            document_file=document_file
        )
        
        return redirect("application-details", id=application_id)
        
    return render(request, "admissions/info/upload_document.html")


def edit_application_document(request):
    if request.method == "POST":
        document_id = request.POST.get("document_id")
        document_type = request.POST.get("document_type")
        document_name = request.POST.get("document_name")
        document_file = request.FILES.get("document_file")
        
        document = ApplicationDocument.objects.get(id=document_id)
        document.document_name = document_name if document_name else document.document_name
        document.document_file = document_file if document_file else document.document_file
        document.document_type = document_type if document_type else document.document_type
        document.save()
        
        return redirect("application-details", id=document.student_application.id)
    return render(request, "admissions/info/edit_document.html")


def delete_application_document(request):
    if request.method == "POST":
        document_id = request.POST.get("document_id")
        document = ApplicationDocument.objects.get(id=document_id)
        document.delete()
        return redirect("application-details", id=document.student_application.id)
    return render(request, "admissions/info/delete_document.html")


def create_education_history(request):
    if request.method == "POST":
        application_id = request.POST.get("application_id")
        institution = request.POST.get("institution")
        level = request.POST.get("level")
        major = request.POST.get("major")
        year = request.POST.get("year")
        grade_or_gpa = request.POST.get("grade_or_gpa")
        
        ApplicationEducationHistory.objects.create(
            student_application_id=application_id,
            institution=institution,
            level=level,
            major=major,
            year=year,
            grade_or_gpa=grade_or_gpa
        )
        return redirect("application-details", id=application_id)
    return render(request, "admissions/info/add_education_history.html")


def edit_education_history(request):
    if request.method == "POST":
        history_id = request.POST.get("history_id")
        institution = request.POST.get("institution")
        level = request.POST.get("level")
        major = request.POST.get("major")
        year = request.POST.get("year")
        grade_or_gpa = request.POST.get("grade_or_gpa")
        
        history = ApplicationEducationHistory.objects.get(id=history_id)
        history.institution = institution if institution else history.institution
        history.level = level if level else history.level
        history.major = major if major else history.major
        history.year = year if year else history.year
        history.grade_or_gpa = grade_or_gpa if grade_or_gpa else history.grade_or_gpa
        history.save()
        return redirect("application-details", id=history.student_application.id)
    return render(request, "admissions/info/edit_education_history.html")


def delete_education_history(request):
    if request.method == "POST":
        history_id = request.POST.get("history_id")
        history = ApplicationEducationHistory.objects.get(id=history_id)
        history.delete()
        return redirect("application-details", id=history.student_application.id)
    return render(request, "admissions/info/delete_education_history.html")


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


def submit_application(request, id):
    application = StudentApplication.objects.get(id=id)
    application.status = "Under Review"
    application.save()
    return redirect("applications")


def accept_application(request, id):
    application = StudentApplication.objects.get(id=id)
    application.status = "Accepted"
    application.save()
    return redirect("application-details", id=application.id)


def apply_for_college(request):
    return render(request, "admissions/apply_for_college.html")


@transaction.atomic
def enroll_applicant(request):
    if request.method == "POST":        
        application_id = request.POST.get("application_id")
        cohort_id = request.POST.get("cohort_id")
        application = StudentApplication.objects.get(id=application_id)
        
        documents = ApplicationDocument.objects.filter(student_application=application)
        eduction_history = ApplicationEducationHistory.objects.filter(student_application=application)
        
        role = UserRole.objects.get(name="Student")
        # Create User
        user = User.objects.create(
            first_name=application.first_name,
            last_name=application.last_name,
            email=application.email,
            phone_number=application.phone_number,
            id_number=application.id_number,
            passport_number=application.passport_number,
            gender=application.gender,
            date_of_birth=application.date_of_birth,
            address=application.address,
            postal_code=application.postal_code,
            city=application.city,
            country=application.country,
            role=role
        )
        
        # Create Student
        student = Student.objects.create(
            user=user,
            registration_number=application.application_number,
            guardian_name=application.guardian_name,
            guardian_email=application.guardian_email,
            guardian_phone_number=application.guardian_phone_number,
            guardian_relationship=application.guardian_relationship,
            programme=application.first_choice_programme,
            status="Active",
            cohort_id=cohort_id
        )
        
        # Create Student Documents
        for document in documents:
            StudentDocument.objects.create(
                student=student,
                document_name=document.document_name,
                document_type=document.document_type,
                document_file=document.document_file
            )
        
        # Create Student Education History
        for history in eduction_history:
            StudentEducationHistory.objects.create(
                student=student,
                institution=history.institution,
                level=history.level,
                major=history.major,
                year=history.year,
                grade_or_gpa=history.grade_or_gpa
            )
            
        # Update Lead if any
        if application.lead:
            application.lead.status = "Converted"
            application.lead.save()
        
        application.status = "Enrolled"
        application.save()
        return redirect("applications")
    return render(request, "admissions/enroll_applicant.html")