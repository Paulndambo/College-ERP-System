from django.urls import path
from apps.staff.views import staff, new_staff, staff_details

urlpatterns = [
    path("", staff, name="staff"),
    path("<int:id>/details/", staff_details, name="staff-details"),
    path("new-staff/", new_staff, name="new-staff"),
]
