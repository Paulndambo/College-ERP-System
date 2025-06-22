from decimal import Decimal
from django.db import models
from django.utils.timezone import now
from datetime import timedelta, date
from apps.core.models import AbsoluteBaseModel
from apps.finance.models import LibraryFinePayment


class Book(AbsoluteBaseModel):
    CATEGORY_CHOICES = [
        ("Book", "Book"),
        ("Journal", "Journal"),
        ("Digital", "Digital"),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    isbn = models.CharField(max_length=13, unique=True, null=True, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    copies_available = models.PositiveIntegerField(default=1)
    total_copies = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=100, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.title} by {self.author}"


class Member(AbsoluteBaseModel):
    ROLE_CHOICES = [
        ("Student", "Student"),
        ("Staff", "Staff"),
    ]
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    date_joined = models.DateField(default=now)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    @property
    def status_text(self):
        return "Active" if self.active else "Inactive"


class BorrowTransaction(AbsoluteBaseModel):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    copy_number = models.CharField(max_length=50, null=True , blank=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    borrow_date = models.DateField(default=date.today)
    due_date = models.DateField(null=True)  # Default 2-week loan
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=255,
        null=True,
        choices=[
            ("Returned", "Returned"),
            ("Pending Return", "Pending Return"),
            ("Lost", "Lost"),
        ],
        default="Pending Return",
    )
    issued_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = now().date() + timedelta(days=14)
        super().save(*args, **kwargs)

    def is_overdue(self):
        if self.return_date:
            return self.return_date > self.due_date
        return date.today() > self.due_date

    def days_overdue(self):
        days_count = 0
        if self.return_date:
            days_count = (self.return_date - self.due_date).days
        days_count = (date.today() - self.due_date).days

        return days_count if days_count > 0 else 0

    def __str__(self):
        return f"{self.book.title} borrowed by {self.member.name}"


class Fine(AbsoluteBaseModel):
    borrow_transaction = models.OneToOneField(
        BorrowTransaction, on_delete=models.CASCADE
    )
    fine_per_day = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.50
    )  # Default $0.50/day
    calculated_fine = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.borrow_transaction.return_date:
            overdue_days = (date.today() - self.borrow_transaction.due_date).days
        else:
            overdue_days = (
                self.borrow_transaction.return_date - self.borrow_transaction.due_date
            ).days

        if overdue_days > 0:
            if self.borrow_transaction.status == "Returned":
                self.calculated_fine = Decimal(overdue_days) * Decimal(self.fine_per_day)
            elif self.borrow_transaction.status == "Lost":
                self.calculated_fine = (
                    Decimal(overdue_days) * Decimal(self.fine_per_day)
                ) + Decimal(self.borrow_transaction.book.unit_price)
        else:
            if self.borrow_transaction.status == "Lost":
                self.calculated_fine = Decimal(self.borrow_transaction.book.unit_price)
            else:
                self.calculated_fine = Decimal(0.00)

        super().save(*args, **kwargs)

    def status_text(self):
        text_value = ""
        fine_payment = LibraryFinePayment.objects.filter(fine=self).first()
        if fine_payment:
            if fine_payment.paid:
                text_value = "Paid"
            else:
                text_value = "Requested"
        else:
            text_value = "Paid" if self.paid else "Unpaid"

        return text_value

    def __str__(self):
        return f"Fine for {self.borrow_transaction.book.title}: ${self.calculated_fine}"
