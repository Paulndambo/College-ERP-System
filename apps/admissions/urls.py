from django.urls import path
from apps.admissions.views import (
    StudentApplicationsListView,
    application_details,
    verify_document,
    apply_for_college,
    start_student_application,
    edit_application
)

urlpatterns = [
    path("applications/", StudentApplicationsListView.as_view(), name="applications"),
    path("applications/<int:id>/details/", application_details, name="application-details"),
    path("verify-document/<int:document_id>/", verify_document, name="verify-document"),
    path("start-application/", start_student_application, name="start-application"),
    path("apply/", apply_for_college, name="apply"),
    path("edit-application/", edit_application, name="edit-application"),
]