from django.urls import path

from apps.staff.leaves.views import (
    CreateLeavePolicyView,
    LeavePoliciesListView,
    LeavePolicyDetailView,
)
from .views import *

urlpatterns = [
    path("list/", StaffListView.as_view(), name="staff"),
    path("active-staff/", ActiveStaffListView.as_view(), name="active-staff"),
    path("positions/", PositionListView.as_view(), name="position-list"),
    path(
        "positions/create/", StaffPositionsCreateView.as_view(), name="position-create"
    ),
    path(
        "positions/<int:pk>/",
        StaffPositionDetailView.as_view(),
        name="position-detail-update-delete",
    ),
    path("create/", CreateStaffView.as_view(), name="create-staff"),
    path("update/<int:pk>/", StaffUpdateView.as_view(), name="update-staff"),
    path("details/<int:pk>/", StaffDetailAPIView.as_view(), name="staff-detail"),
    path(
        "status/<int:pk>/toggle-status/",
        StaffStatusToggleView.as_view(),
        name="staff-toggle-status",
    ),
    path("details/<int:pk>/", StaffUpdateView.as_view(), name="staff-detail-update"),
    # path(
    #     "payroll/detail/<int:pk>/",
    #     StaffPayrollDetailView.as_view(),
    #     name="detail-staff-payroll",
    # ),
    # path("payroll/", StaffPayrollListView.as_view(), name="payroll-list"),
    # path("payroll/create/", StaffPayrollCreateView.as_view(), name="payroll-create"),
    # path(
    #     "payroll/<int:pk>/",
    #     StaffPayrollUpdateView.as_view(),
    #     name="payroll-detail-update",
    # ),
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
    # leaves
    path("leave-policies/", LeavePoliciesListView.as_view(), name="leave-policies"),
    path(
        "leave-policies/<int:pk>/",
        LeavePolicyDetailView.as_view(),
        name="leave-policy-detail",
    ),
    path(
        "leave-policies/create/",
        CreateLeavePolicyView.as_view(),
        name="leave-policies-create",
    ),
    path("leaves/", StaffLeaveListView.as_view(), name="staff-leaves"),
    path(
        "leave-applications/",
        StaffLeaveApplicationListView.as_view(),
        name="leave-applications",
    ),
    path(
        "leave-applications/create/",
        StaffLeaveApplicationCreateView.as_view(),
        name="leave-application-create",
    ),
    path(
        "leave-applications/<int:pk>/",
        StaffLeaveApplicationUpdateView.as_view(),
        name="leave-application-update",
    ),
    path(
        "leave-entitlements/",
        StaffLeaveEntitlementListView.as_view(),
        name="staff-entitlements-list",
    ),
    path(
        "leave-entitlements/create/",
        StaffLeaveEntitlementCreateView.as_view(),
        name="leave-entitlements-create",
    ),
    path(
        "leave-entitlements/bulk-create/",
        StaffLeaveEntitlementBulkCreateView.as_view(),
        name="leave-entitlements-bulk-create",
    ),
    path(
        "leave-entitlements/<int:pk>/update/",
        StaffLeaveEntitlementUpdateView.as_view(),
        name="leave-application-update",
    ),
    path(
        "overtime-payments/",
        OvertimePaymentsAPIView.as_view(),
        name="overtime-payments-list",
    ),
    path(
        "overtime-payments/<int:pk>/update/",
        OvertimePaymentsUpdateView.as_view(),
        name="overtime-payments",
    ),
    path(
        "overtime-payments/create/",
        OvertimePaymentCreateView.as_view(),
        name="overtime-payments-create",
    ),
    path(
        "overtime-payments/<int:pk>/approve/",
        ApproveOvertimeRecordView.as_view(),
        name="approve-overtime",
    ),
]
