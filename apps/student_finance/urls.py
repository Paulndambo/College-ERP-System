from django.urls import path

from apps.student_finance.views import (
    CreateInvoiceTypeView,
    InvoiceTypeDetailView,
    InvoiceTypesListView,
    StudentFeeInvoiceListView,
    StudentFeePaymentListView,
    StudentFeePaymentView,
    StudentFeeStatementListView,
    TotalCollectedFeesView,
)

urlpatterns = [
    path("invoices/", StudentFeeInvoiceListView.as_view(), name="fee-invoices"),
    path("invoice-types/", InvoiceTypesListView.as_view(), name="invoice-types-list"),
    path("invoice-types/create/", CreateInvoiceTypeView.as_view(), name="invoice-type-create"),
    path("invoice-types/<int:pk>/", InvoiceTypeDetailView.as_view(), name="invoice-detail-update-delete"),
    path("fee-payments/", StudentFeePaymentView.as_view(), name="student-fee-payment"),
    path(
        "fee-payments-list/", StudentFeePaymentListView.as_view(), name="fee-payments"
    ),
    path(
        "fee-statements/", StudentFeeStatementListView.as_view(), name="fee-statements"
    ),
    path(
        "total-fees-collected/",
        TotalCollectedFeesView.as_view(),
        name="total-collected-fees",
    ),
]
