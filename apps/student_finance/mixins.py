from django.db import transaction
from apps.student_finance.models import (
    StudentFeeInvoice,
    StudentFeePayment,
    StudentFeeStatement,
    StudentFeeLedger,
)
from apps.schools.models import Semester
from apps.students.models import Student
from apps.finance.models import FeeStructure
import logging
from datetime import date
from decimal import Decimal
from django.db.models import Sum, F

logging.basicConfig(level=logging.DEBUG)

from apps.core.constants import payment_ref_generator


class StudentInvoicingMixin(object):
    def __init__(
        self, student, semester, transaction_type, amount, payment_method=None
    ):
        self.student = student
        self.semester = semester
        self.transaction_type = transaction_type
        self.amount = amount
        self.payment_method = payment_method

    @transaction.atomic()
    def run(self):
        if "invoice" in self.transaction_type.lower():
            message = f"""
                Student: ID: {self.student.id} Name: {self.student.name()},
                Semester: ID: {self.semester.id} Name: {self.semester.name},
                Transaction Type: {self.transaction_type},
                Amount: {self.amount}
            """
            print(message)
            return self.__invoice_student()
        else:
            return self.__process_fees_payment()

    def __get_current_balance(self):
        """Get the current balance for the student"""
        last_statement = (
            StudentFeeStatement.objects.filter(student=self.student)
            .order_by("-created_on")
            .first()
        )
        return last_statement.balance if last_statement else Decimal("0.00")

    def __process_fees_payment(self):
        try:
            StudentFeePayment.objects.create(
                student=self.student,
                amount=self.amount,
                payment_date=date.today(),
                payment_method=self.payment_method,
            )

            current_balance = self.__get_current_balance()

            unpaid_invoices = StudentFeeInvoice.objects.filter(
                student=self.student, status__in=["Pending", "Partially Paid"]
            ).order_by("created_on")

            remaining_amount = self.amount
            applied_amount = Decimal("0.00")

            for invoice in unpaid_invoices:
                if remaining_amount <= 0:
                    break

                balance_due = invoice.bal_due

                if remaining_amount >= balance_due:
                    invoice.amount_paid += balance_due
                    invoice.status = "Paid"
                    applied_amount += balance_due
                    remaining_amount -= balance_due
                else:
                    invoice.amount_paid += remaining_amount
                    invoice.status = "Partially Paid"
                    applied_amount += remaining_amount
                    remaining_amount = Decimal("0.00")

                invoice.save()

            # total_outstanding = StudentFeeInvoice.objects.filter(
            #     student=self.student,
            #     status__in=["Pending", "Partially Paid"]
            # ).aggregate(
            #     total_due=Sum(F('amount') - F('amount_paid'))
            # )['total_due'] or Decimal("0.00")

            # If there's remaining payment amount after covering invoices or arrears it becomes the new balance in fee statement
            new_balance = current_balance - self.amount

            print(f"Current balance: {current_balance}")
            print(f"Payment amount: {self.amount}")
            print(f"Amount applied to invoices: {applied_amount}")
            print(f"Remaining amount (overpayment): {remaining_amount}")
            print(f"New balance: {new_balance}")

            # Create fee statement
            StudentFeeStatement.objects.create(
                student=self.student,
                debit=Decimal("0.00"),
                credit=self.amount,
                balance=new_balance,
                statement_type="Payment",
                transaction_type="Student Payment",
                semester=self.semester if self.semester else None,
                payment_method=self.payment_method,
            )

            logging.info("Student payment processed and invoices updated.")

        except Exception as e:
            logging.error(f"Error processing payment: {e}")
            raise
        return True

    def __invoice_student(self):
        try:
            ref = payment_ref_generator()

            StudentFeeInvoice.objects.create(
                amount=self.amount,
                reference=ref,
                semester_id=self.semester.id,
                student_id=self.student.id,
                description=self.transaction_type,
            )

            last_fee_stmt = (
                StudentFeeStatement.objects.filter(student=self.student)
                .order_by("-created_on")
                .first()
            )

            new_balance = self.amount
            if last_fee_stmt:
                new_balance += last_fee_stmt.balance

            StudentFeeStatement.objects.create(
                debit=self.amount,
                credit=0,
                balance=new_balance,
                student_id=self.student.id,
                statement_type="Invoice",
                transaction_type=self.transaction_type,
                semester_id=self.semester.id,
            )

            logging.INFO("Student Invoicing ended successfully!!!!!!!!!!!!!!!")

        except Exception as e:
            logging.error(e)
        finally:
            logging.info("Student Invoicing ended successfully!!!!!!!!!!!!!!!")
            return True


class ActiveStudentsInvoicingMixin(object):
    def __init__(self, semester):
        self.semester = semester

    def run(self):
        students = Student.objects.filter(status="Active")
        for student in students:
            fee_structure = FeeStructure.objects.filter
            StudentInvoicingMixin(student, self.semester, "Invoice", 1000).run()

        return True
