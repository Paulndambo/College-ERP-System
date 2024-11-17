from django.urls import path
from apps.students.views import (
    students,
    edit_student,
    student_details,
    new_student,
    meal_cards,
    delete_student,
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
]
