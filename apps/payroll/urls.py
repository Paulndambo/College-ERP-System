from django.urls import path
from .views import PayWagesCreateAPIView, RunPayrollAPIView

urlpatterns = [
    path("process-payroll/", RunPayrollAPIView.as_view(), name="process-payroll"),
    path("pay-wages/", PayWagesCreateAPIView.as_view(), name="pay-wages"),
]
