from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from datetime import datetime

from apps.payroll.mixins.PayWagesMixin import PayWagesService
from apps.payroll.process_payslips import process_payroll_monthly_period
from apps.payroll.serializers import PayWagesCreateSerializer
from apps.payroll.utils.payment import generate_payment_reference
from services.constants import ALL_STAFF_ROLES
from services.permissions import HasUserRole
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions

from django.shortcuts import get_object_or_404

from apps.staff.models import Payslip


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


class PayWagesCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=PayWagesCreateSerializer)
    def post(self, request):
        serializer = PayWagesCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payslip = serializer.validated_data["payslip"]
        amount = serializer.validated_data["amount"]
        payment_method = serializer.validated_data["payment_method"]
        notes = serializer.validated_data.get("notes", "")

        reference = generate_payment_reference(
            staff_no=payslip.staff.staff_number, prefix="SAL"
        )
        service = PayWagesService(
            payslip=payslip,
            amount=amount,
            payment_method=payment_method,
            reference=reference,
            user=self.request.user,
            notes=notes,
        )

        try:
            payment = service.process_payment()
            return Response(
                {
                    "message": "Wage payment processed successfully.",
                    "payment_id": payment.id,
                    "reference": payment.payment_reference,
                    "amount": str(payment.amount_paid),
                    "paid_by": self.request.user.username,
                    "payment_method": payment.payment_method,
                    "staff": str(payment.payslip.staff),
                    "payslip_id": payment.payslip.id,
                    "payslip_status": payment.payslip.payment_status,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
