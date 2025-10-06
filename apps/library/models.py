from decimal import Decimal
from django.db import models
from django.utils.timezone import now
from datetime import timedelta, date
from apps.core.models import AbsoluteBaseModel
from apps.finance.models import LibraryFinePayment


class LibraryConfig(AbsoluteBaseModel):
    name = models.CharField(max_length=100)  # e.g., "Staff Borrowing Rules"
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class LibraryConfigRule(AbsoluteBaseModel):
    RULE_TYPE_CHOICES = [
        ("Borrow", "Borrowing Rule"),
        ("Fine", "Fine Rule"),
        ("Other", "Other"),
    ]

    library_config = models.ForeignKey(
        LibraryConfig, on_delete=models.CASCADE, related_name="rules"
    )
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES)
    name = models.CharField(
        max_length=100
    )  # e.g., "Default Borrow Days", "Max Renewals"

    borrow_days = models.PositiveIntegerField(
        null=True, blank=True, help_text="Number of days allowed to borrow"
    )
    max_renewals = models.PositiveIntegerField(
        null=True, blank=True, help_text="Maximum times a book can be renewed"
    )
    fine_per_day = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Fine charged per day",
    )
    rule_notes = models.TextField(null=True, blank=True, help_text="Optional notes")

    def __str__(self):
        return f"{self.library_config.name} - {self.name}"


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
    book = models.ForeignKey("Book", on_delete=models.CASCADE)
    copy_number = models.CharField(max_length=50, null=True, blank=True)
    member = models.ForeignKey("Member", on_delete=models.CASCADE)
    borrow_date = models.DateField(default=date.today)
    due_date = models.DateField(null=True)
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

    # Renewal tracking
    renewal_count = models.PositiveIntegerField(default=0)
    max_renewals = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.book.title} borrowed by {self.member.user.first_name}"


class Fine(AbsoluteBaseModel):
    STATUS_CHOICES = [
        ("Upaid", "Unpaid"),
        ("Requested", "Requested"),
        ("Paid", "Paid"),
    ]

    borrow_transaction = models.OneToOneField(
        "BorrowTransaction", on_delete=models.CASCADE
    )
    calculated_fine = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Unpaid")

    @property
    def member_name(self):
        return f"{self.borrow_transaction.member.user.first_name} {self.borrow_transaction.member.user.last_name}"

    @property
    def book_title(self):
        return self.borrow_transaction.book.title

    @property
    def is_paid(self):
        return self.status == "Paid"

    @property
    def is_overdue(self):
        borrow = self.borrow_transaction
        if borrow.return_date:
            return borrow.return_date > borrow.due_date
        return (
            False if borrow.due_date is None else borrow.due_date < borrow.borrow_date
        )

    def __str__(self):
        return f"Fine for {self.book_title}: ${self.calculated_fine} - {self.status}"
