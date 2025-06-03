from django.urls import path
from .views import *

urlpatterns = [
    path("staff/list", StaffListView.as_view(), name="staff"),
    path("staff/create/", CreateStaffView.as_view(), name="create-staff"),
    path("staff/update/<int:pk>/", StaffUpdateView.as_view(), name="update-staff"),
    path("staff-account/update/<int:pk>/", StaffAccountUpdateView.as_view(), name="update-staff-account"),
    
]
