from django.urls import path
from apps.studentsportal.views import (
    StudentFeesPaymentsAPIView, StudentFeeInvoicesAPIView,
    StudentFeeLedgerAPIView, StudentFeeStatementAPIView
)

from apps.studentsportal.students.views import (
    MealCardAPIView, StudentAttendanceAPIView, SemesterReportingAPIView
)

urlpatterns = [
    path('fees-payments/', StudentFeesPaymentsAPIView.as_view(), name='student-fees-payments'),
    path('fees-invoices/', StudentFeeInvoicesAPIView.as_view(), name='student-fees-invoices'),
    path('fees-ledger/', StudentFeeLedgerAPIView.as_view(), name='student-fees-ledger'),
    path('fees-statement/', StudentFeeStatementAPIView.as_view(), name='student-fees-statement'),

    path('student-meal-cards/', MealCardAPIView.as_view(), name='student-meal-cards'),
    path('class-attendances/', StudentAttendanceAPIView.as_view(), name='student-attendances'),
    path('semester-reportings/', SemesterReportingAPIView.as_view(), name='semester-reportings'),
]