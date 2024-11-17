from django.urls import path
from apps.staff.views import staff, new_staff

urlpatterns = [
    path("", staff, name="staff"),
    path("new-staff/", new_staff, name="new-staff"),
]
