from django.urls import path
from apps.students.views import (
    students,
    edit_student,
    student_details,
    new_student,
    delete_student,
    edit_student_cohort,
    create_education_history,
    delete_education_history,
    edit_education_history,
    StudentListView,
)

from apps.students.uploads.views import upload_students
from apps.students.attendance.views import (
    AttendanceDashboardListView,
    CohortAttendanceDetailView,
)
from apps.students.checkins.views import (
    StudentCheckInListView,
    checkin_student,
    checkout_student,
    delete_checkin_record,
)

from apps.students.mealcards.views import MealCardsListView, new_meal_card

urlpatterns = [
    path("", StudentListView.as_view(), name="students"),
    path("<int:student_id>/details/", student_details, name="student-details"),
    path("new-student/", new_student, name="new-student"),
    path("edit-student/", edit_student, name="edit-student"),
    path("edit-student-cohort/", edit_student_cohort, name="edit-student-cohort"),
    path("delete-student/", delete_student, name="delete-student"),
    path("upload-students/", upload_students, name="upload-students"),
    path(
        "create-education-history/",
        create_education_history,
        name="create-education-history",
    ),
    path(
        "edit-student-education-history/",
        edit_education_history,
        name="edit-student-education-history",
    ),
    path(
        "delete-education-history/",
        delete_education_history,
        name="delete-education-history",
    ),
    path(
        "attendance-dashboard/",
        AttendanceDashboardListView.as_view(),
        name="attendance-dashboard",
    ),
    path(
        "attendance-dashboard/<int:cohort_id>/",
        CohortAttendanceDetailView.as_view(),
        name="cohort-attendance-dashboard",
    ),
    path(
        "student-checkins/", StudentCheckInListView.as_view(), name="student-checkins"
    ),
    path("checkin-student/", checkin_student, name="checkin-student"),
    path("checkout-student/<int:id>/", checkout_student, name="checkout-student"),
    path("delete-checkin-record/", delete_checkin_record, name="delete-checkin-record"),
    path("meal-cards/", MealCardsListView.as_view(), name="meal-cards"),
    path("new-mealcard/", new_meal_card, name="new-mealcard"),
]
