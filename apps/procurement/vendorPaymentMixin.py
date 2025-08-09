from django.db import transaction
from decimal import Decimal
from datetime import date
import logging

from apps.procurement.models import VendorPayment, VendorPaymentStatement

logger = logging.getLogger(__name__)


class VendorPaymentService:
    def __init__(
        self, tender_award, amount, payment_method, reference, user, description=""
    ):
        self.tender_award = tender_award
        self.vendor = tender_award.vendor
        self.amount = Decimal(str(amount))
        self.payment_method = payment_method
        self.reference = reference
        self.user = user
        self.description = description

    @transaction.atomic
    def process_payment(self):
        """Process vendor payment and update balances"""
        try:

            if self.amount <= 0:
                raise ValueError("Payment amount must be greater than zero")

            if self.amount > self.tender_award.balance_due:
                raise ValueError("Payment amount cannot exceed balance due")

            logger.info(f"tender_award in mixin: {self.tender_award}")
            logger.info(f"vendor in mixin: {self.tender_award.vendor}")
            payment = VendorPayment.objects.create(
                tender_award=self.tender_award,
                amount=self.amount,
                payment_method=self.payment_method,
                reference=self.reference,
                description=(
                    f"Payment - {self.description}" if self.description else "Payment"
                ),
                paid_by=self.user,
            )

            self.tender_award.amount_paid += self.amount
            self.tender_award.save()

            current_balance = self._get_current_balance()
            new_balance = current_balance - self.amount

            VendorPaymentStatement.objects.create(
                vendor=self.vendor,
                tender_award=self.tender_award,
                statement_type="Payment",
                credit=self.amount,
                balance=new_balance,
                description=(
                    f"Payment - {self.description}" if self.description else "Payment"
                ),
                payment_method=self.payment_method,
            )

            logger.info(f"Vendor payment processed successfully: {payment}")
            return payment

        except Exception as e:
            logger.error(f"Error processing vendor payment: {e}")
            raise

    def _get_current_balance(self):
        """Get current balance for this tender award"""
        last_statement = (
            VendorPaymentStatement.objects.filter(
                vendor=self.vendor, tender_award=self.tender_award
            )
            .order_by("-created_on")
            .first()
        )

        if last_statement:
            return last_statement.balance
        else:
            return self.tender_award.award_amount
