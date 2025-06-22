from django.urls import path
from .views import (
    CampusCreateView,
    CampusListView,
    CampusUpdateDeleteView,
    StudyYearCreateView,
    StudyYearListView,
    StudyYearUpdateDeleteView,
    UserRoleListView,
)

urlpatterns = [
    path("campus/create/", CampusCreateView.as_view(), name="campus-create"),
    path("campus/list/", CampusListView.as_view(), name="campus-list"),
    path("user-roles/", UserRoleListView.as_view(), name="user-role-list"),
    path(
        "campus/update-delete/<int:pk>/",
        CampusUpdateDeleteView.as_view(),
        name="campus-update-delete",
    ),
    path("studyyear/create/", StudyYearCreateView.as_view(), name="studyyear-create"),
    path("studyyear/list/", StudyYearListView.as_view(), name="studyyear-list"),
    path(
        "studyyear/update-delete/<int:pk>/",
        StudyYearUpdateDeleteView.as_view(),
        name="studyyear-update-delete",
    ),
]
