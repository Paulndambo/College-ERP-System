from django.urls import path
from apps.staff.views import (
    StaffListView,
    LeavesListView,
    LeaveApplicationListView,
    cancel_leave,
    complete_leave,
    leave_details,
    leave_application_details,
    new_staff,
    staff_details,
    new_leave_application,
    edit_leave_application,
    approve_leave_application,
    decline_leave_application,
)

urlpatterns = [
    path("", StaffListView.as_view(), name="staff"),
    path("<int:id>/details/", staff_details, name="staff-details"),
    path("new-staff/", new_staff, name="new-staff"),
    path("leaves/", LeavesListView.as_view(), name="leaves"),
    path("leaves/<int:id>/details/", leave_details, name="leave-details"),
    path("cancel-leave", cancel_leave, name="cancel-leave"),
    path("complete-leave/", complete_leave, name="complete-leave"),
    path(
        "leave-applications/",
        LeaveApplicationListView.as_view(),
        name="leave-applications",
    ),
    path(
        "leave-applications/<int:id>/details/",
        leave_application_details,
        name="leave-application-details",
    ),
    path("new-leave-application/", new_leave_application, name="new-leave-application"),
    path(
        "edit-leave-application/", edit_leave_application, name="edit-leave-application"
    ),
    path(
        "approve-leave-application/",
        approve_leave_application,
        name="approve-leave-application",
    ),
    path(
        "decline-leave-application/",
        decline_leave_application,
        name="decline-leave-application",
    ),
]
