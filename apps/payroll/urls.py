from django.urls import path
from .views import RunPayrollAPIView

urlpatterns = [
    path("process-payroll/", RunPayrollAPIView.as_view(), name="process-payroll"),
]
