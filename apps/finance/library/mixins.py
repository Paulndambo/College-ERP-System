from datetime import date
from decimal import Decimal
import logging

from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.library.models import Fine, LibraryFinePayment
from apps.core.constants import payment_ref_generator

logger = logging.getLogger(__name__)


class ProcessLibraryPaymentMixin:
    def __init__(self, fine_id, amount, payment_method, current_user):
        self.fine_id = fine_id
        self.amount = Decimal(amount)
        self.payment_method = payment_method
        self.current_user = current_user
        self.fine = None
        self.member = None

    @transaction.atomic
    def run(self):
        self.__fetch_fine()

        if self.fine.paid:
            raise ValueError("Fine has already been paid.")

        if LibraryFinePayment.objects.filter(fine=self.fine).exists():
            raise ValueError("Payment for this fine already exists.")

        if self.amount < self.fine.calculated_fine:
            raise ValueError("Amount must be equal to or greater than the fine amount.")

        return self.__process_payment()

    def __fetch_fine(self):
        self.fine = get_object_or_404(Fine, id=self.fine_id)
        self.member = self.fine.borrow_transaction.member
        logger.info(f"Fetched fine ID {self.fine.id} for member {self.member.id}")

    def __process_payment(self):
        ref = payment_ref_generator()

        payment = LibraryFinePayment.objects.create(
            member=self.member,
            fine=self.fine,
            amount=self.amount,
            payment_date=date.today(),
            payment_method=self.payment_method,
            payment_reference=ref,
            recorded_by=self.current_user,
            paid=False,
        )

        self.fine.paid = True
        self.fine.save()

        payment.paid = True
        payment.save()

        logger.info(f"Library fine {self.fine.id} fully paid. Payment ID: {payment.id}")

        return {
            "fine_id": self.fine.id,
            "member": self.member.user.first_name,
            "total_fine": float(self.fine.calculated_fine),
            "amount_paid": float(self.amount),
            "fine_paid_status": self.fine.paid,
            "payment_id": payment.id,
            "payment_reference": payment.payment_reference,
        }
