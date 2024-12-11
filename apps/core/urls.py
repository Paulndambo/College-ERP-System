from django.urls import path
from apps.core.views import (
    home,
    campuses,
    delete_campus,
    edit_campus,
    new_campus,
    study_years,
    new_study_year,
    edit_study_year,
    delete_study_year,
)

urlpatterns = [
    path("", home, name="home"),
    path("campuses/", campuses, name="campuses"),
    path("delete-campus/", delete_campus, name="delete-campus"),
    path("edit-campus/", edit_campus, name="edit-campus"),
    path("new-campus/", new_campus, name="new-campus"),
    path("study-years/", study_years, name="study-years"),
    path("new-year/", new_study_year, name="new-year"),
    path("edit-year/", edit_study_year, name="edit-year"),
    path("delete-year/", delete_study_year, name="delete-year"),
]
