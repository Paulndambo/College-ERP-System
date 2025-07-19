from django.urls import path
from .views import (
    ProgammeDetailView,
    SchoolCreateView,
    SchoolListView,
    SchoolUpdateDeleteView,
    DepartmentCreateView,
    DepartmentListView,
    DepartmentUpdateDeleteView,
    ProgrammeCreateView,
    ProgrammeListView,
    ProgrammeUpdateDeleteView,
    CourseCreateView,
    CourseListView,
    CourseUpdateDeleteView,
    SemesterCreateView,
    SemesterListView,
    SemesterUpdateDeleteView,
    ProgrammeCohortCreateView,
    ProgrammeCohortListView,
    ProgrammeCohortUpdateDeleteView,
    CourseSessionCreateView,
    CourseSessionListView,
    CourseSessionUpdateDeleteView,
)

urlpatterns = [
    path("school/create/", SchoolCreateView.as_view(), name="school-create"),
    path("school/list/", SchoolListView.as_view(), name="school-list"),
    path(
        "school/update-delete/<int:pk>/",
        SchoolUpdateDeleteView.as_view(),
        name="school-update-delete",
    ),
    path(
        "department/create/", DepartmentCreateView.as_view(), name="department-create"
    ),
    path("department/list/", DepartmentListView.as_view(), name="department-list"),
    path(
        "department/update-delete/<int:pk>/",
        DepartmentUpdateDeleteView.as_view(),
        name="department-update-delete",
    ),
    path("programme/create/", ProgrammeCreateView.as_view(), name="programme-create"),
    path("programme/list/", ProgrammeListView.as_view(), name="programme-list"),
    path("programme/<int:pk>/", ProgammeDetailView.as_view(), name="programme-details"),
    path(
        "programme/update-delete/<int:pk>/",
        ProgrammeUpdateDeleteView.as_view(),
        name="programme-update-delete",
    ),
    path("course/create/", CourseCreateView.as_view(), name="course-create"),
    path("course/list/", CourseListView.as_view(), name="course-list"),
    path(
        "course/update-delete/<int:pk>/",
        CourseUpdateDeleteView.as_view(),
        name="course-update-delete",
    ),
    path("semester/create/", SemesterCreateView.as_view(), name="semester-create"),
    path("semester/list/", SemesterListView.as_view(), name="semester-list"),
    path(
        "semester/update-delete/<int:pk>/",
        SemesterUpdateDeleteView.as_view(),
        name="semester-update-delete",
    ),
    path(
        "programme-cohort/create/",
        ProgrammeCohortCreateView.as_view(),
        name="programme-cohort-create",
    ),
    path(
        "programme-cohort/list/",
        ProgrammeCohortListView.as_view(),
        name="programme-cohort-list",
    ),
    path(
        "programme-cohort/update-delete/<int:pk>/",
        ProgrammeCohortUpdateDeleteView.as_view(),
        name="programme-cohort-update-delete",
    ),
    path(
        "course-session/create/",
        CourseSessionCreateView.as_view(),
        name="course-session-create",
    ),
    path(
        "course-session/list/",
        CourseSessionListView.as_view(),
        name="course-session-list",
    ),
    path(
        "course-session/update-delete/<int:pk>/",
        CourseSessionUpdateDeleteView.as_view(),
        name="course-session-update-delete",
    ),
]
