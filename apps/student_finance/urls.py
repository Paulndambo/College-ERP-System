from django.urls import path

from apps.student_finance.billing.views import BulkFeeInvoiceView, BulkInvoiceView, FeePaymentView, FeeStatementReportsAPIView, SingleInvoiceView, SingleStudentFeeInvoiceView
from apps.student_finance.views import (
    CreateInvoiceTypeView,
    FeeStatementsView,
    InvoiceTypeDetailView,
    InvoiceTypesListView,
    StudentFeeInvoiceListView,
    StudentFeePaymentListView,
    StudentFeeStatementListView,
    TotalCollectedFeesView,
)

urlpatterns = [
    path("invoices/", StudentFeeInvoiceListView.as_view(), name="fee-invoices"),
    path("invoice-types/", InvoiceTypesListView.as_view(), name="invoice-types-list"),
    path(
        "invoice-types/create/",
        CreateInvoiceTypeView.as_view(),
        name="invoice-type-create",
    ),
    path(
        "invoice-types/<int:pk>/",
        InvoiceTypeDetailView.as_view(),
        name="invoice-detail-update-delete",
    ),
    # path("fee-payments/", StudentFeePaymentView.as_view(), name="student-fee-payment"),
    path(
        "fee-payments-list/", StudentFeePaymentListView.as_view(), name="fee-payments"
    ),
    path(
        "fee-statements/", StudentFeeStatementListView.as_view(), name="fee-statements"
    ),
    path(
        "all-fee-statements/", FeeStatementsView.as_view(), name="fee-statements"
    ),
    path(
        "total-fees-collected/",
        TotalCollectedFeesView.as_view(),
        name="total-collected-fees",
    ),
    
     # Generate invoices from FeeStructure for all students in a class
    path("bulk-fee-invoices/", BulkFeeInvoiceView.as_view(), name="bulk-fee-invoices"),

    # Generate invoice from FeeStructure for a single student
    path("single-student-fee-invoice/", SingleStudentFeeInvoiceView.as_view(), name="single-student-fee-invoice"),

    # Create ad-hoc invoice for a single student (amount provided)
    path("single-invoice/", SingleInvoiceView.as_view(), name="single-invoice"),

    # Create ad-hoc invoices for all students in a class (amount provided)
    path("bulk-invoice/", BulkInvoiceView.as_view(), name="bulk-invoice"),
    path("fee-payments/", FeePaymentView.as_view(), name="fee-payment"),
    path("fee-statements-reports/", FeeStatementReportsAPIView.as_view(), name="fee-statameents-report"),
]
