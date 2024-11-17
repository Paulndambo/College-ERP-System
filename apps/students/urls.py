from django.urls import path
from apps.students.views import (
    students,
    edit_student,
    student_details,
    new_student,
    meal_cards,
    delete_student,
    
    create_education_history,
    delete_education_history,
    edit_education_history,
)

from apps.students.uploads.views import upload_students

urlpatterns = [
    path("", students, name="students"),
    path("<int:student_id>/details/", student_details, name="student-details"),
    path("new-student/", new_student, name="new-student"),
    path("edit-student/", edit_student, name="edit-student"),
    path("meal-cards/", meal_cards, name="meal-cards"),
    path("delete-student/", delete_student, name="delete-student"),
    path("upload-students/", upload_students, name="upload-students"),

    path("create-education-history/", create_education_history, name="create-education-history"),
    path("edit-education-history/", edit_education_history, name="edit-education-history"),
    path("delete-education-history/", delete_education_history, name="delete-education-history"),
]
