from django.urls import path
from apps.schools.views import (
    schools,
    school_details,
    new_school,
    delete_school,
    edit_school,
    courses,
    new_course,
    edit_course,
    delete_course,
    programmes,
    programme_details,
    new_programme,
    edit_programme,
    delete_programme,
    departments,
    department_details,
    new_department,
    edit_department,
    delete_department,
)


urlpatterns = [
    path("", schools, name="schools"),
    path("<int:id>/", school_details, name="school-details"),
    path("new-school/", new_school, name="new-school"),
    path("delete-school/", delete_school, name="delete-school"),
    path("edit-school/", edit_school, name="edit-school"),
    path("courses/", courses, name="courses"),
    path("edit-course/", edit_course, name="edit-course"),
    path("new-course/", new_course, name="new-course"),
    path("delete-course/", delete_course, name="delete-course"),
    path("programmes/", programmes, name="programmes"),
    path("programmes/<int:id>/details/", programme_details, name="programme-details"),
    path("edit-programme/", edit_programme, name="edit-programme"),
    path("new-programme/", new_programme, name="new-programme"),
    path("delete-programme/", delete_programme, name="delete-programme"),
    path("departments/", departments, name="departments"),
    path(
        "departments/<int:id>/details/", department_details, name="department-details"
    ),
    path("new-department/", new_department, name="new-department"),
    path("edit-department/", edit_department, name="edit-department"),
    path("delete-department/", delete_department, name="delete-department"),
]
