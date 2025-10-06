from decimal import Decimal
from datetime import date
import logging

from django.db import transaction
from apps.finance.models import FeeStructure
from apps.student_finance.models import (
    StudentFeeInvoice,
    StudentFeePayment,
    StudentFeeStatement,
)
from apps.student_finance.utils.payment_reference_generator import payment_ref_generator
from apps.students.models import Student

logging.basicConfig(level=logging.DEBUG)


class PaymentProcessor:
    """Handles student fee payments"""

    def __init__(
        self,
        student,
        amount,
        payment_method,
        semester,
        description=None,
        reference=None,
        user=None,
    ):
        self.student = student
        self.amount = Decimal(amount)
        self.payment_method = payment_method
        self.semester = semester
        self.user = user
        self.description = description
        self.reference = reference

    def _get_last_balance(self):
        last_statement = (
            StudentFeeStatement.objects.filter(student=self.student)
            .order_by("-created_on")
            .first()
        )
        return last_statement.balance if last_statement else Decimal("0.00")

    @transaction.atomic
    def process(self):
        try:
            # 1. Record raw payment
            payment = StudentFeePayment.objects.create(
                student=self.student,
                amount=self.amount,
                payment_date=date.today(),
                payment_method=self.payment_method,
                created_by=self.user,
                reference=self.reference
                or payment_ref_generator(suffix="CASH"),
            )

            last_balance = self._get_last_balance()
            remaining_amount = self.amount
            applied_amount = Decimal("0.00")

            # 2. Apply payment to unpaid invoices (oldest first)
            unpaid_invoices = StudentFeeInvoice.objects.filter(
                student=self.student, status__in=["Pending", "Partially Paid"]
            ).order_by("created_on")

            for invoice in unpaid_invoices:
                if remaining_amount <= 0:
                    break

                balance_due = invoice.bal_due
                allocation = min(balance_due, remaining_amount)

                invoice.amount_paid += allocation
                invoice.status = (
                    "Paid"
                    if invoice.amount_paid >= invoice.amount
                    else "Partially Paid"
                )
                invoice.save()

                # StudentFeePaymentInvoice.objects.create(
                #     payment=payment,
                #     invoice=invoice,
                #     amount_applied=allocation,
                # )

                applied_amount += allocation
                remaining_amount -= allocation

            # 3. Update running balance
            new_balance = last_balance - self.amount

            # 4. Record statement
            StudentFeeStatement.objects.create(
                student=self.student,
                debit=Decimal("0.00"),
                credit=self.amount,
                balance=new_balance,
                statement_type="Payment",
                # invoice_type=None,  # Payment doesn’t directly belong to an invoice_type
                semester=self.semester,
                payment_method=self.payment_method,
                # description=self.description if self.description else "Fees Payment",
            )

            logging.info(
                f"Payment processed: student={self.student}, applied={applied_amount}, "
                f"remaining={remaining_amount}, new_balance={new_balance}"
            )
            return payment

        except Exception as e:
            logging.error(f"Error processing payment: {e}")
            raise


class InvoiceProcessor:
    """Handles student invoicing (single and bulk, resolves amount from FeeStructure if not provided)"""

    def __init__(
        self,
        student,
        semester,
        invoice_type,
        amount=None,
        user=None,
        cohort=None,
        
    ):
        self.student = student
        self.semester = semester
        self.invoice_type = invoice_type
        # amount may be None -> resolved later
        self.amount = Decimal(amount) if amount is not None else None
        # cohort can be passed explicitly (useful for bulk or historical invoices)
        self.cohort = cohort or (
            getattr(student, "cohort", None) if student else None
        )
        self.user = user

    def _get_last_balance(self):
        last_statement = (
            StudentFeeStatement.objects.filter(student=self.student)
            .order_by("-created_on")
            .first()
        )
        return last_statement.balance if last_statement else Decimal("0.00")

    def _resolve_amount(self):
        """If amount is not passed, derive from FeeStructure for cohort + semester."""
        if self.amount is not None:
            return self.amount

        if not self.cohort:
            logging.error("cohort is required but not provided for invoicing.")
            return None

        try:
            fee_structure = FeeStructure.objects.get(
                programme=self.cohort.programme,
                year_of_study=self.cohort.current_year,
                semester=self.semester
            )
            return Decimal(fee_structure.total_amount())

        except FeeStructure.DoesNotExist:
            logging.error(
                f"No FeeStructure found for programme={self.cohort.programme}, "
                f"year_of_study={self.cohort.current_year}, semester={self.semester}"
            )
            return None


    @transaction.atomic
    def create_invoice(self):
        amount = self._resolve_amount()
        ref = payment_ref_generator(suffix="INV", model=StudentFeeInvoice)
        if amount is None:
            logging.error(
                "Invoice creation aborted — no fee structure or amount provided"
            )
            return None
        invoice = StudentFeeInvoice.objects.create(
            amount=amount,
            reference=ref,
            semester=self.semester,
            student=self.student,
            invoice_type=self.invoice_type,
            created_by=self.user,
        )

        last_balance = self._get_last_balance()
        new_balance = last_balance + amount

        StudentFeeStatement.objects.create(
            debit=amount,
            credit=Decimal("0.00"),
            balance=new_balance,
            student=self.student,
            statement_type="Invoice",
            # invoice_type=self.invoice_type,
            semester=self.semester,
        )

        logging.info(
            f"Invoice created: ref={invoice.reference}, student={self.student}, type={self.invoice_type}, amount={amount}"
        )
        return invoice

    @classmethod
    def single_fee_invoice(
        cls, student, invoice_type, semester, user, cohort=None, amount=None
    ):
        """Generate invoice for a single student (amount auto from FeeStructure if not given)."""
        processor = cls(
            student=student,
            semester=semester,
            invoice_type=invoice_type,
            amount=amount,
            user=user,
            cohort=cohort or student.cohort,
        )
        return processor.create_invoice()

    @classmethod
    def bulk_fee_invoice(cls, cohort, semester, invoice_type, user, amount=None,batch_size=100,):
        """
        Generate invoices for all students in the given cohort.
        If amount is None, the FeeStructure for (cohort, semester) will be used to resolve amount.
        The entire bulk operation is atomic.
        """
        logging.info(
        "[START] Generating invoices | cohort=%s, semester=%s, invoice_type=%s, user=%s",
        cohort, semester, invoice_type, user
        )
        # students = Student.objects.filter(cohort=cohort)
        try:
            students_qs = Student.objects.filter(cohort=cohort)
            count = students_qs.count()
            logging.info("Found %d students for cohort=%s", count, cohort)

            if count == 0:
                logging.warning("No students found for cohort=%s", cohort)
                return []

            invoices = []
            batch = []

            # Wrap entire operation in a transaction
            with transaction.atomic():
                for idx, student in enumerate(students_qs.iterator(chunk_size=batch_size), start=1):
                    # Check for existing invoice for same semester + type
                    if StudentFeeInvoice.objects.filter(
                            student=student, semester=semester, invoice_type=invoice_type
                        ).exists():
                            logging.info(
                                "Skipping student #%d (%s) — already invoiced for %s / %s",
                                idx, student, semester, invoice_type
                            )
                            continue

                    logging.debug("Queuing student #%d: %s", idx, student)

                    processor = cls(
                        student=student,
                        semester=semester,
                        invoice_type=invoice_type,
                        amount=amount,
                        user=user,
                        cohort=cohort,
                    )
                    batch.append(processor)

                    if len(batch) >= batch_size:
                        logging.info("Processing batch of %d invoices...", len(batch))
                        with transaction.atomic():
                            for p in batch:
                                try:
                                    inv = p.create_invoice()
                                    invoices.append(inv)
                                    logging.debug("Invoice created: %s", inv.reference)
                                except Exception as e:
                                    logging.exception(
                                        "Error creating invoice for student %s: %s",
                                        student, e
                                    )
                        batch.clear()

                # process any remaining
                if batch:
                    logging.info("Processing final batch of %d invoices...", len(batch))
                    with transaction.atomic():
                        for p in batch:
                            try:
                                inv = p.create_invoice()
                                invoices.append(inv)
                                logging.debug("Invoice created: %s", inv.reference)
                            except Exception as e:
                                logging.exception(
                                    "Error creating invoice for student %s: %s",
                                    p.student, e
                                )

            logging.info("[END] Successfully created %d invoices.", len(invoices))
            return invoices

        except Exception as e:
            logging.exception("Bulk invoice generation failed: %s", e)
            raise

class StudentInvoicingMixin:
    """Delegates to PaymentProcessor or InvoiceProcessor"""

    def __init__(
        self,
        student=None,
        cohort=None,
        semester=None,
        invoice_type=None,
        amount=None,
        payment_method=None,
        user=None,
        action=None,
        reference=None,
    ):
        self.student = student
        self.cohort = cohort
        self.semester = semester
        self.invoice_type = invoice_type
        self.amount = amount
        self.payment_method = payment_method
        self.user = user
        self.action = action
        self.reference = reference

    def _process(self):
        if self.action == "invoice":
            # bulk invoice for a cohort
            if self.cohort:
                return InvoiceProcessor.bulk_fee_invoice(
                    cohort=self.cohort,
                    semester=self.semester,
                    invoice_type=self.invoice_type,
                    amount=self.amount,  # can be None -> resolved from FeeStructure
                    user=self.user,
                )

            # single invoice for a student (amount None => resolved from FeeStructure using cohort)
            elif self.student:
                return InvoiceProcessor.single_fee_invoice(
                    student=self.student,
                    semester=self.semester,
                    invoice_type=self.invoice_type,
                    amount=self.amount,  # can be None
                    user=self.user,
                    cohort=self.cohort
                    or getattr(self.student, "cohort", None),
                )

            else:
                # raise ValueError("Must provide either student or cohort for invoicing.")
                logging.error(
                    "Must provide either student or cohort for invoicing."
                )
                return None

        elif self.action == "payment":
            if not self.student:
                raise ValueError("Payment requires a student.")
            return PaymentProcessor(
                student=self.student,
                amount=self.amount,
                payment_method=self.payment_method,
                semester=self.semester,
                user=self.user,
                reference=self.reference,
            ).process()

        else:
            raise ValueError("Invalid action. Must be 'invoice' or 'payment'.")
