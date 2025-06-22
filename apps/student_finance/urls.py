from django.urls import path

from apps.student_finance.views import StudentFeeInvoiceListView, StudentFeePaymentListView, StudentFeePaymentView

urlpatterns =[
    path("invoices/", StudentFeeInvoiceListView.as_view(), name="fee-invoices"),
    path("fee-payments/", StudentFeePaymentView.as_view(), name="student-fee-payment"),
    path("fee-payments-list/", StudentFeePaymentListView.as_view(), name="fee-payments"),
]