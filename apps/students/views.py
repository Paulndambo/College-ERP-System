from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages

from django.views.generic import ListView
from django.http import JsonResponse
from django.db.models import Q


from apps.students.models import Student, StudentDocument, MealCard, StudentEducationHistory
from apps.users.models import User
from apps.core.models import UserRole
from apps.schools.models import Programme, ProgrammeCohort


# Create your views here.
EDUCATION_LEVELS = ["Primary School", "Secondary School", "College", "University"]
GRADUATION_STATUSES = ["Graduated", "Not Graduated"]
GUARDIAN_RELATIONSHIPS = ["Parent", "Grand Parent", "Sibling", "Aunt/Uncle", "Other"]
def students(request):
    students = Student.objects.all().order_by("-created_on")

    if request.method == "POST":
        search_text = request.POST.get("search_text")
        if search_text:
            students = Student.objects.filter(
                Q(user__first_name__icontains=search_text)
                | Q(user__last_name__icontains=search_text)
                | Q(registration_number__icontains=search_text)
            )

    paginator = Paginator(students, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    programmes = Programme.objects.all().order_by("-created_on")

    context = {"page_obj": page_obj, "programmes": programmes, "relationship_choices": GUARDIAN_RELATIONSHIPS}
    return render(request, "students/students.html", context)

programmes = Programme.objects.all().order_by("-created_on")
class StudentListView(ListView):
    model = Student
    template_name = 'students/students.html'
    context_object_name = 'students'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) |
                Q(registration_number__icontains=search_query) |
                Q(user__first_name__icontains=search_query)
            )
        
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context["relationship_choices"] = GUARDIAN_RELATIONSHIPS
        context["programmes"] = programmes
        return context
    

def student_details(request, student_id):
    student = Student.objects.get(id=student_id)
    
    cohorts = ProgrammeCohort.objects.all().order_by("-created_on")
    
    education_history = StudentEducationHistory.objects.filter(student_id=student_id).order_by("-created_on")
    context = {"student": student, "education_history": education_history, "cohorts": cohorts, "levels": EDUCATION_LEVELS, "statuses": GRADUATION_STATUSES}
    
    return render(request, "students/student_details.html", context)


def new_student(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        gender = request.POST.get("gender")
        phone_number = request.POST.get("phone_number")
        address = request.POST.get("address")
        city = request.POST.get("city")
        country = request.POST.get("country")

        registration_number = request.POST.get("registration_number")
        guardian_name = request.POST.get("guardian_name")
        guardian_phone_number = request.POST.get("guardian_phone_number")

        programme_id = request.POST.get("programme_id")

        user_role = UserRole.objects.get(name="Student")

        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=registration_number,
            role=user_role,
            phone_number=phone_number,
            address=address,
            city=city,
            country=country,
            gender=gender,
        )

        student = Student.objects.create(
            user=user,
            registration_number=registration_number,
            guardian_name=guardian_name,
            guardian_phone_number=guardian_phone_number,
            programme_id=programme_id,
            status="Active",
        )
        messages.success(request, "Student created successfully.")
        return redirect("students")
    return render(request, "students/new_student.html")


def edit_student(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        gender = request.POST.get("gender")
        phone_number = request.POST.get("phone_number")
        address = request.POST.get("address")
        postal_code = request.POST.get("postal_code")
        city = request.POST.get("city")
        state = request.POST.get("state")
        country = request.POST.get("country")

        registration_number = request.POST.get("registration_number")
        guardian_name = request.POST.get("guardian_name")
        guardian_phone_number = request.POST.get("guardian_phone_number")
        guardian_email = request.POST.get("guardian_email")
        guardian_relationship = request.POST.get("guardian_relationship")
        

        student = Student.objects.get(id=student_id)
        user = User.objects.get(id=student.user.id)

        user.first_name = first_name if first_name else user.first_name
        user.last_name = last_name if last_name else user.last_name
        user.email = email if email else user.email
        user.phone_number = phone_number if phone_number else user.phone_number
        user.address = address if address else user.address
        user.city = city if city else user.city
        user.country = country if country else user.country
        user.gender = gender if gender else user.gender
        user.postal_code = postal_code if postal_code else user.postal_code
        user.state = state if state else user.state
        user.save()

        student.registration_number = registration_number if registration_number else student.registration_number
        student.guardian_name = guardian_name if guardian_name else student.guardian_name
        student.guardian_phone_number = guardian_phone_number if guardian_phone_number else student.guardian_phone_number
        student.guardian_email = guardian_email if guardian_email else student.guardian_email
        student.guardian_relationship = guardian_relationship if guardian_relationship else student.guardian_relationship
        student.save()

        return redirect(f"/students/{student.id}/details")
    return render(request, "students/edit_student.html")


def edit_student_cohort(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        cohort_id = request.POST.get("cohort_id")
        
        student = Student.objects.get(id=student_id)
        cohort = ProgrammeCohort.objects.get(id=cohort_id)
        student.cohort = cohort
        student.programme = cohort.programme
        student.save()
        return redirect(f"/students/{student.id}/details")
    return render(request, "students/edit_student_cohort.html")

def delete_student(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        student = Student.objects.get(id=student_id)
        student.delete()

        return redirect("students")
    return render(request, "students/delete_student.html")


def meal_cards(request):
    meal_cards = MealCard.objects.all().order_by("-created_on")

    paginator = Paginator(meal_cards, 7)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}
    return render(request, "mealcards/mealcards.html", context)


# Education History
def create_education_history(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        institution = request.POST.get("institution")
        level = request.POST.get("level")
        graduated = request.POST.get("graduated")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        StudentEducationHistory.objects.create(
            student_id=student_id,
            institution=institution,
            level=level,
            start_date=start_date,
            end_date=end_date,
            graduated=True if graduated == "Graduated" else False,
        )
        return redirect(f"/students/{student_id}/details/")
    return render(request, "education_history/create_education_history.html")

def edit_education_history(request):
    if request.method == "POST":
        education_history_id = request.POST.get("education_history_id")
        institution = request.POST.get("institution")
        level = request.POST.get("level")
        graduated = request.POST.get("graduated")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        education_history = StudentEducationHistory.objects.get(id=education_history_id)
        education_history.institution = institution
        education_history.level = level
        education_history.start_date = start_date
        education_history.end_date = end_date
        education_history.graduated = True if graduated == "Graduated" else False

        education_history.save()
        return redirect(f"/students/{education_history.student.id}/details/")
    return render(request, "education_history/edit_education_history.html")


def delete_education_history(request):
    if request.method == "POST":
        education_history_id = request.POST.get("education_history_id")
        education_history = StudentEducationHistory.objects.get(id=education_history_id)
        education_history.delete()
        return redirect(f"/students/{education_history.student.id}/details/")
    return render(request, "education_history/delete_education_history.html")