from django.shortcuts import render, redirect
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from django.db import transaction

from django.views.generic import ListView
from django.http import JsonResponse

from apps.schools.models import School, Department, Programme, Course, Semester

# Create your views here.
PROGRAMME_TYPES = ["Artisan", "Certificate", "Diploma", "Bachelor", "Masters", "PhD"]

SEMESTER_STATUSES = ["Active", "Closed"]
### Schools
def schools(request):
    schools = School.objects.all().order_by("-created_on")

    if request.method == "POST":
        search_text = request.POST.get("search_text")
        schools = School.objects.filter(Q(name__icontains=search_text))

    paginator = Paginator(schools, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}
    return render(request, "schools/schools.html", context)


def school_details(request, id):
    school = School.objects.get(id=id)

    departments = Department.objects.filter(school=school)

    paginator = Paginator(departments, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"school": school, "page_obj": page_obj}
    return render(request, "schools/school_details.html", context)


def new_school(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        location = request.POST.get("location")

        School.objects.create(name=name, email=email, phone=phone, location=location)

        return redirect("schools")

    return render(request, "schools/new_school.html")


def edit_school(request):
    if request.method == "POST":
        school_id = request.POST.get("school_id")
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        location = request.POST.get("location")

        school = School.objects.get(id=school_id)

        school.name = name
        school.email = email
        school.phone = phone
        school.location = location
        school.save()

        return redirect("schools")
    return render(request, "schools/edit_school.html")


def delete_school(request):
    if request.method == "POST":
        school_id = request.POST.get("school_id")
        school = School.objects.get(id=school_id)
        school.delete()

        return redirect("schools")
    return render(request, "schools/delete_school.html")


### Departments
def departments(request):
    departments = Department.objects.all().order_by("-created_on")

    if request.method == "POST":
        search_text = request.POST.get("search_text")
        departments = Department.objects.filter(
            Q(name__icontains=search_text) | Q(school__name__icontains=search_text)
        )

    paginator = Paginator(departments, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}
    return render(request, "departments/departments.html", context)


def department_details(request, id):
    department = Department.objects.get(id=id)

    programmes = Programme.objects.filter(department=department).order_by("-created_on")

    if request.method == "POST":
        search_text = request.POST.get("search_text")
        programmes = Programme.objects.filter(Q(name__icontains=search_text))

    paginator = Paginator(programmes, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "department": department,
        "levels": PROGRAMME_TYPES,
        "page_obj": page_obj,
    }
    return render(request, "departments/department_details.html", context)


def new_department(request):
    if request.method == "POST":
        name = request.POST.get("name")
        school_id = request.POST.get("school_id")
        office = request.POST.get("office")

        Department.objects.create(name=name, school_id=school_id, office=office)

        return redirect(f"/schools/{school_id}")

    return render(request, "departments/new_department.html")


def edit_department(request):
    if request.method == "POST":
        department_id = request.POST.get("department_id")
        name = request.POST.get("name")
        school_id = request.POST.get("school_id")
        office = request.POST.get("office")

        department = Department.objects.get(id=department_id)

        department.name = name
        department.school_id = school_id
        department.office = office
        department.save()

        return redirect("departments")
    return render(request, "departments/edit_department.html")


def delete_department(request):
    if request.method == "POST":
        department_id = request.POST.get("department_id")
        department = Department.objects.get(id=department_id)
        department.delete()

        return redirect("departments")
    return render(request, "departments/delete_department.html")


### Programmes
class ProgrammesListView(ListView):
    model = Programme
    template_name = 'programmes/programmes.html'
    context_object_name = 'programmes'
    paginate_by = 8
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) |
                Q(name__icontains=search_query) 
            )
        
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context["levels"] = PROGRAMME_TYPES
        return context


def programme_details(request, id):
    programme = Programme.objects.get(id=id)

    courses = Course.objects.filter(programme=programme).order_by("-created_on")

    paginator = Paginator(courses, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"programme": programme, "page_obj": page_obj}
    return render(request, "programmes/programme_details.html", context)


def new_programme(request):
    if request.method == "POST":
        name = request.POST.get("name")
        department_id = request.POST.get("department_id")
        level = request.POST.get("level")
        code = request.POST.get("code")

        department = Department.objects.get(id=department_id)
        Programme.objects.create(
            name=name,
            department=department,
            school=department.school,
            level=level,
            code=code,
        )
        return redirect(f"/schools/departments/{department_id}/details")

    return render(request, "programmes/new_programme.html")


def edit_programme(request):
    if request.method == "POST":
        programme_id = request.POST.get("programme_id")
        name = request.POST.get("name")
        level = request.POST.get("level")
        code = request.POST.get("code")

        programme = Programme.objects.get(id=programme_id)

        programme.name = name
        programme.department = programme.department
        programme.school = programme.department.school
        programme.level = level
        programme.code = code
        programme.save()

        return redirect("programmes")
    return render(request, "programmes/edit_programme.html")


def delete_programme(request):
    if request.method == "POST":
        programme_id = request.POST.get("programme_id")
        programme = Programme.objects.get(id=programme_id)
        programme.delete()

        return redirect("programmes")
    return render(request, "programmes/delete_programme.html")


### Courses
class CoursesListView(ListView):
    model = Course
    template_name = 'courses/courses.html'
    context_object_name = 'courses'
    paginate_by = 8
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(course_code__icontains=search_query) |
                Q(programme__name__icontains=search_query)
            )
        
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context
    

def new_course(request):
    if request.method == "POST":
        name = request.POST.get("name")
        course_code = request.POST.get("course_code")
        programme_id = request.POST.get("programme_id")

        programme = Programme.objects.get(id=programme_id)
        Course.objects.create(
            name=name,
            department=programme.department,
            programme=programme,
            school=programme.department.school,
            course_code=course_code,
        )
        return redirect(f"/schools/programmes/{programme_id}/details")

    return render(request, "courses/new_course.html")


def edit_course(request):
    if request.method == "POST":
        course_id = request.POST.get("course_id")
        name = request.POST.get("name")
        course_code = request.POST.get("course_code")
        programme_id = request.POST.get("programme_id")

        programme = Programme.objects.get(id=programme_id)
        course = Course.objects.get(id=course_id)

        course.name = name
        course.department = programme.department
        course.school = programme.department.school
        course.programme = programme
        course.code = course_code
        course.save()

        return redirect("courses")
    return render(request, "courses/edit_course.html")


def delete_course(request):
    if request.method == "POST":
        course_id = request.POST.get("course_id")
        course = Course.objects.get(id=course_id)
        course.delete()

        return redirect("courses")
    return render(request, "courses/delete_course.html")

# Semesters
class SemestersListView(ListView):
    model = Semester
    template_name = 'semesters/semesters.html'
    context_object_name = 'semesters'
    paginate_by = 8
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) |
                Q(name__icontains=search_query) 
            )
        
        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context["semester_statuses"] = SEMESTER_STATUSES
        return context
    
    
def new_semester(request):
    if request.method == "POST":
        name = request.POST.get("name")
        academic_year = request.POST.get("academic_year")
        status = request.POST.get("status")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        Semester.objects.create(name=name, academic_year=academic_year, status=status, start_date=start_date, end_date=end_date)
        return redirect("semesters")

    return render(request, "semesters/new_semester.html")


def edit_semester(request):
    if request.method == "POST":
        semester_id = request.POST.get("semester_id")
        name = request.POST.get("name")
        academic_year = request.POST.get("academic_year")
        status = request.POST.get("status")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        semester = Semester.objects.get(id=semester_id)

        semester.name = name
        semester.academic_year = academic_year
        semester.status = status
        semester.start_date = start_date
        semester.end_date = end_date
        semester.save()

        return redirect("semesters")
    return render(request, "semesters/edit_semester.html")


def delete_semester(request):
    if request.method == "POST":
        semester_id = request.POST.get("semester_id")
        semester = Semester.objects.get(id=semester_id)
        semester.delete()

        return redirect("semesters")
    return render(request, "semesters/delete_semester.html")