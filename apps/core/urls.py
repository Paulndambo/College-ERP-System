from django.urls import path
from apps.core.views import home, campuses, delete_campus, edit_campus, new_campus

urlpatterns = [
    path("", home, name="home"),
    path("campuses/", campuses, name="campuses"),
    path("delete-campus/", delete_campus, name="delete-campus"),
    path("edit-campus/", edit_campus, name="edit-campus"),
    path("new-campus/", new_campus, name="new-campus"),
]
