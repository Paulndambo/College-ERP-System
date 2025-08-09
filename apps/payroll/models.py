from django.db import models

from apps.core.models import AbsoluteBaseModel


# Create your models here.
class PaymentStatement(AbsoluteBaseModel):
    """Track payment statements/schedules for payslips that may have multiple payments"""

    payslip = models.OneToOneField(
        "staff.Payslip", on_delete=models.CASCADE, related_name="payment_statement"
    )
    total_amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    outstanding_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment Statement - {self.payslip.staff} ({self.total_amount_paid}/{self.total_amount_due})"


class SalaryPayment(AbsoluteBaseModel):
    """Model to track individual salary payments made to staff - supports multiple payments per payslip"""

    PAYMENT_METHOD_CHOICES = [
        ("Cash", "Cash"),
        ("Bank", "Bank Transfer"),
        ("Mpesa", "Mpesa"),
        ("Cheque", "Cheque"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    payslip = models.ForeignKey(
        "staff.Payslip", on_delete=models.CASCADE, related_name="salary_payments"
    )
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHOD_CHOICES, default="bank"
    )
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Transaction ID, cheque number, etc.",
    )
    journal_entry = models.ForeignKey(
        "accounting.JournalEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="salary_payments",
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default="completed"
    )
    notes = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"Payment for {self.payslip.staff} - {self.amount_paid}"
