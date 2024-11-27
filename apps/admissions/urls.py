from django.urls import path
from apps.admissions.views import (
    StudentApplicationsListView,
    application_details,
    verify_document,
    apply_for_college,
    start_student_application,
    edit_application,
    upload_application_document,
    edit_application_document,
    delete_application_document,
    create_education_history,
    edit_education_history,
    delete_education_history,
    submit_application,
    enroll_applicant,
    accept_application,
)

urlpatterns = [
    path("applications/", StudentApplicationsListView.as_view(), name="applications"),
    path(
        "applications/<int:id>/details/",
        application_details,
        name="application-details",
    ),
    path("verify-document/<int:document_id>/", verify_document, name="verify-document"),
    path("start-application/", start_student_application, name="start-application"),
    path("apply/", apply_for_college, name="apply"),
    path("edit-application/", edit_application, name="edit-application"),
    path("submit-application/<int:id>/", submit_application, name="submit-application"),
    path("accept-application/<int:id>/", accept_application, name="accept-application"),
    path(
        "upload-application-document/",
        upload_application_document,
        name="upload-application-document",
    ),
    path(
        "edit-application-document/",
        edit_application_document,
        name="edit-application-document",
    ),
    path(
        "delete-application-document/",
        delete_application_document,
        name="delete-application-document",
    ),
    path(
        "add-education-history/", create_education_history, name="add-education-history"
    ),
    path(
        "edit-education-history/", edit_education_history, name="edit-education-history"
    ),
    path(
        "delete-education-history/",
        delete_education_history,
        name="delete-education-history",
    ),
    path("enroll-applicant/", enroll_applicant, name="enroll-applicant"),
]
