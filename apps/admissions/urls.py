from django.urls import path
from apps.admissions.views import (
    StudentApplicationsListView,
    application_details
)

urlpatterns = [
    path("applications/", StudentApplicationsListView.as_view(), name="applications"),
    path("applications/<int:id>/details/", application_details, name="application-details"),
]