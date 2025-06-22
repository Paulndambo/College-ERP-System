from django.urls import path
from .views import *

urlpatterns = [
    path("list/", StaffListView.as_view(), name="staff"),
    path("positions/", PositionListView.as_view(), name="position-list"),
    path("create/", CreateStaffView.as_view(), name="create-staff"),
    path("update/<int:pk>/", StaffUpdateView.as_view(), name="update-staff"),
    path("details/<int:pk>/", StaffDetailAPIView.as_view(), name="staff-detail"),
    path(
        "status/<int:pk>/toggle-status/",
        StaffStatusToggleView.as_view(),
        name="staff-toggle-status",
    ),
    path(
        "onboarding-progress/<int:pk>/",
        StaffOnboardingProgressAPIView.as_view(),
        name="onboarding progress",
    ),
    path(
        "onboarding-progress/<int:pk>/complete/",
        CompleteOnboardingView.as_view(),
        name="complete-onboarding",
    ),
    path("details/<int:pk>/", StaffUpdateView.as_view(), name="staff-detail-update"),
    path(
        "payroll/detail/<int:pk>/",
        StaffPayrollDetailView.as_view(),
        name="detail-staff-payroll",
    ),
    path("payroll/", StaffPayrollListView.as_view(), name="payroll-list"),
    path("payroll/create/", StaffPayrollCreateView.as_view(), name="payroll-create"),
    path(
        "payroll/<int:pk>/",
        StaffPayrollUpdateView.as_view(),
        name="payroll-detail-update",
    ),
    path("documents/", StaffDocumentListView.as_view(), name="documents-list"),
    path("payslips/", StaffPaySlipListView.as_view(), name="payslips-list"),
    path(
        "documents/create/", StaffDocumentCreateView.as_view(), name="documents-create"
    ),
    path(
        "documents/<int:pk>/",
        StaffDocumentUpdateView.as_view(),
        name="documents-detail-update",
    ),
    
    
    #leaves
    path("leaves/", StaffLeaveListView.as_view(), name="staff-leaves"),
    path("leave-applications/", StaffLeaveApplicationListView.as_view(), name="leave-applications"),
    path("leave-applications/create/", StaffLeaveApplicationCreateView.as_view(), name="leave-application-create"),
    path("leave-applications/<int:pk>/", StaffLeaveApplicationUpdateView.as_view(), name="leave-application-update")
]
