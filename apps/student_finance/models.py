from decimal import Decimal
from django.db import models
from apps.core.models import AbsoluteBaseModel

from uuid import uuid4

# Create your models here.
STUDENT_FEES_TRANSACTION_TYPES = (
    ("Standard Invoice", "Standard Invoice"),
    ("Student Payment", "Student Payment"),
    ("Trip Invoice", "Trip Invoice"),
    ("Graduation Invoice", "Graduation Invoice"),
)

STUDENT_INVOICE_TYPES = (
    ("Standard Invoice", "Standard Invoice"),
    ("Trip Invoice", "Trip Invoice"),
    ("Graduation Invoice", "Graduation Invoice"),
)

STUDENT_FEE_STATEMENT_TYPES = (
    ("Invoice", "Invoice"),
    ("Payment", "Payment"),
)
class InvoiceType(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_fee_type = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class StudentFeeInvoice(AbsoluteBaseModel):
    reference = models.CharField(max_length=255, null=True)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    # description = models.CharField(
    #     max_length=255, choices=STUDENT_INVOICE_TYPES, default="Standard Invoice"
    # )
    invoice_type = models.ForeignKey(
        "InvoiceType", on_delete=models.SET_NULL, null=True, blank=True
    )
    semester = models.ForeignKey(
        "schools.Semester", on_delete=models.SET_NULL, null=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0")
    )
    status = models.CharField(
        max_length=255,
        default="Pending",
        choices=(
            ("Pending", "Pending"),
            ("Paid", "Paid"),
            ("Partially Paid", "Partially Paid"),
        ),
    )
    created_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, blank=True
    )

    @property
    def bal_due(self):
        return self.amount - self.amount_paid

    def __str__(self):
        return self.reference


class StudentFeePayment(AbsoluteBaseModel):
    reference = models.CharField(max_length=255, null=True, blank=True)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(
        max_length=255,
        choices=(
            ("Mpesa", "Mpesa"),
            ("Bank Transfer", "Bank Transfer"),
            ("Cash", "Cash"),
        ),
    )
    created_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.student.registration_number
    
    def save(self, *args, **kwargs):
        last_payment = StudentFeePayment.objects.filter(student=self.student).last()
        if last_payment and not self.reference:
            self.reference = f"FP-{uuid4().hex[:8].upper()}-{last_payment.id + 1}"
        elif not self.reference:
            self.reference = f"FP-{uuid4().hex[:8].upper()}-1"
        else:
            self.reference = f"FP-{uuid4().hex[:8].upper()}"
        return super().save(*args, **kwargs)


class StudentFeeLedger(AbsoluteBaseModel):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    transaction_type = models.CharField(
        max_length=255, choices=STUDENT_FEES_TRANSACTION_TYPES
    )
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))

    def __str__(self):
        return self.student.registration_number


class StudentFeeStatement(AbsoluteBaseModel):
    PAYMENT_METHODS = StudentFeePayment._meta.get_field("payment_method").choices
    reference = models.CharField(max_length=255, null=True, blank=True)
    payment_method = models.CharField(max_length=255, choices=PAYMENT_METHODS, null=True, blank=True)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    statement_type = models.CharField(max_length=255, choices=STUDENT_FEE_STATEMENT_TYPES)
    # transaction_type = models.CharField(max_length=255, choices=STUDENT_FEES_TRANSACTION_TYPES, default="Standard Invoice")
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    semester = models.ForeignKey(
        "schools.Semester", on_delete=models.SET_NULL, null=True
    )

    @property
    def academic_year(self):
        return self.semester.academic_year

    def __str__(self):
        return self.student.registration_number
    
    def save(self, *args, **kwargs):
        last_statement = StudentFeeStatement.objects.filter(student=self.student).last()
        if last_statement and not self.reference:
            self.reference = f"FS-{uuid4().hex[:8].upper()}-{last_statement.id + 1}"
        else:
            self.reference = f"FS-{uuid4().hex[:8].upper()}"
        return super().save(*args, **kwargs)
