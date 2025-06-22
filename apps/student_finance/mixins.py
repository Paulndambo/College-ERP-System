from django.db import transaction
from apps.student_finance.models import StudentFeeInvoice, StudentFeeStatement
import logging

logging.basicConfig(level=logging.DEBUG)

from apps.core.constants import payment_ref_generator

class StudentInvoicingMixin(object):
    def __init__(self, student, semester, transaction_type, amount):
        self.student = student
        self.semester = semester
        self.transaction_type = transaction_type
        self.amount = amount
        
    @transaction.atomic()
    def run(self):
        if "invoice" in self.transaction_type.lower():
            self.__invoice_student()
        else:
            self.__process_fees_payment()
    
    def __process_fees_payment(self):
        pass
    
    def __invoice_student(self):
        logging.INFO("Student Invoicing Started...!!!!!!!!!!!")
        try:
            ref = payment_ref_generator()
            
            StudentFeeInvoice.objects.create(
                amount=self.amount,
                reference=ref,
                semester=self.semester,
                student=self.student,
                description=self.transaction_type
            )
            
            last_fee_stmt = StudentFeeStatement.objects.filter(student=self.student).order_by("-created").first()
                
            if not last_fee_stmt:
                StudentFeeStatement.objects.create(
                    debit=self.amount,
                    balance=self.amount,
                    credit=0,
                    student=self.student,
                    statement_type="Invoice",
                    transaction_type="Standard Invoice"
                )
                
            else:
                StudentFeeStatement.objects.create(
                    debit=self.amount,
                    balance=self.amount + last_fee_stmt.balance,
                    credit=0,
                    student=self.student,
                    statement_type="Invoice",
                    transaction_type="Standard Invoice"
                )
            logging.INFO("Student Invoicing ended successfully!!!!!!!!!!!!!!!")
            return True
        except Exception as e:
            logging.error(e)