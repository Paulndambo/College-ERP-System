from django.urls import path
from . import views

app_name = "admissions"

urlpatterns = [
    path("intakes/", views.IntakeListView.as_view(), name="intake-list"),
    path("intakes/<int:pk>/", views.IntakeDetailView.as_view(), name="intake-detail"),
    path("intakes/create/", views.IntakeCreateView.as_view(), name="intake-create"),
    path(
        "intakes/<int:pk>/update/",
        views.IntakeUpdateView.as_view(),
        name="intake-update",
    ),
    path(
        "applications/list/",
        views.StudentApplicationListView.as_view(),
        name="application-list",
    ),
    path(
        "applications/details/<int:pk>/",
        views.StudentApplicationDetailView.as_view(),
        name="application-detail",
    ),
    path(
        "applications/create/",
        views.StudentApplicationCreateView.as_view(),
        name="application-create",
    ),
    path(
        "applications/<int:pk>/update/",
        views.StudentApplicationUpdateView.as_view(),
        name="application-update",
    ),
    path(
        "applications/enroll-student/",
        views.StudentEnrollmentView.as_view(),
        name="enroll-student",
    ),
    path(
        "documents/", views.ApplicationDocumentListView.as_view(), name="document-list"
    ),
    path(
        "documents/<int:pk>/",
        views.ApplicationDocumentDetailView.as_view(),
        name="document-detail",
    ),
    path(
        "documents/create/",
        views.ApplicationDocumentCreateView.as_view(),
        name="document-create",
    ),
    path(
        "documents/<int:pk>/update/",
        views.ApplicationDocumentUpdateView.as_view(),
        name="document-update",
    ),
    path(
        "education-history/",
        views.ApplicationEducationHistoryListView.as_view(),
        name="education-history-list",
    ),
    path(
        "education-history/<int:pk>/",
        views.ApplicationEducationHistoryDetailView.as_view(),
        name="education-history-detail",
    ),
    path(
        "education-history/create/",
        views.ApplicationEducationHistoryCreateView.as_view(),
        name="education-history-create",
    ),
    path(
        "education-history/<int:pk>/update/",
        views.ApplicationEducationHistoryUpdateView.as_view(),
        name="education-history-update",
    ),
    path(
        "enrollments-metrics/",
        views.EnrollmentsByIntakeView.as_view(),
        name="enrollments-metrics",
    ),
]
