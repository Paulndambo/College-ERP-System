from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

from apps.payroll.process_payslips import process_payroll_monthly_period
from services.constants import ALL_STAFF_ROLES
from services.permissions import HasUserRole


class RunPayrollAPIView(APIView):
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES

    def post(self, request, *args, **kwargs):
        start_date_str = request.data.get("start_date")
        end_date_str = request.data.get("end_date")

        if not start_date_str or not end_date_str:
            return Response(
                {"error": "start_date and end_date are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payroll_period_start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            payroll_period_end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Dates must be in YYYY-MM-DD format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        process_payroll_monthly_period(payroll_period_start, payroll_period_end)

        return Response(
            {"message": "Payroll run successfully."}, status=status.HTTP_200_OK
        )
