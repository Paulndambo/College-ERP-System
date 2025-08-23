from django.db import transaction
from decimal import Decimal
import logging

from apps.payroll.models import PaymentStatement, SalaryPayment
from apps.staff.models import Payslip

logger = logging.getLogger(__name__)


class PayWagesService:
    def __init__(self, payslip, amount, payment_method, reference, user, notes=""):
        self.payslip = payslip
        self.staff = payslip.staff
        self.amount = Decimal(str(amount))
        self.payment_method = payment_method
        self.reference = reference
        self.user = user
        self.notes = notes

    @transaction.atomic
    def process_payment(self):
        """Process salary payment for a staff member and update balances."""
        try:
            if self.amount <= 0:
                raise ValueError("Payment amount must be greater than zero")

            payment_statement = self._get_or_create_statement()

            if self.amount > payment_statement.outstanding_balance:
                raise ValueError("Payment amount cannot exceed outstanding balance")

            # Create salary payment record
            payment = SalaryPayment.objects.create(
                payslip=self.payslip,
                payment_method=self.payment_method,
                payment_reference=self.reference,
                amount_paid=self.amount,
                payment_status="completed",
                notes=self.notes,
                processed_by=self.user,
            )

            # Update payment statement
            payment_statement.total_amount_paid += self.amount
            payment_statement.outstanding_balance -= self.amount
            payment_statement.save()

            # Update payslip payment status
            self._update_payslip_status(payment_statement)

            logger.info(f"Salary payment processed successfully: {payment}")
            return payment

        except Exception as e:
            logger.error(f"Error processing salary payment: {e}")
            raise

    def _get_or_create_statement(self):
        """Get or create the payment statement for this payslip."""
        statement, created = PaymentStatement.objects.get_or_create(
            payslip=self.payslip,
            defaults={
                "total_amount_due": self.payslip.net_pay,
                "outstanding_balance": self.payslip.net_pay,
            },
        )
        return statement

    def _update_payslip_status(self, statement):
        """Update payslip payment status based on the outstanding balance."""
        if statement.outstanding_balance <= 0:
            self.payslip.payment_status = "paid"
        elif statement.total_amount_paid > 0:
            self.payslip.payment_status = "partially_paid"
        else:
            self.payslip.payment_status = "pending"
        self.payslip.save()
