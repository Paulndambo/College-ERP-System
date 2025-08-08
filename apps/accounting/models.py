from django.db import models

from apps.core.models import AbsoluteBaseModel


class ActiveAccountManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_archived=False)


class AccountType(AbsoluteBaseModel):
    name = models.CharField(max_length=50, unique=True)
    normal_balance = models.CharField(
        max_length=6, choices=[("debit", "Debit"), ("credit", "Credit")]
    )
    is_archived = models.BooleanField(default=False)
    active = ActiveAccountManager()
    all_objects = models.Manager()

    objects = active

    def __str__(self):
        return self.name


class Account(AbsoluteBaseModel):
    account_code = models.CharField(max_length=10, unique=True)  # e.g. '1001'
    name = models.CharField(max_length=100)  # e.g. 'Cash at Bank'
    account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE)
    is_default = models.BooleanField(default=False)
    is_contra = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    normal_balance = models.CharField(
        max_length=6,
        choices=[("debit", "Debit"), ("credit", "Credit")],
        editable=False,
        null=True,
        blank=True,
    )
    cash_flow_section = models.CharField(
        max_length=20,
        choices=[
            ("Operating", "Operating"),
            ("Investing", "Investing"),
            ("Financing", "Financing"),
        ],
        null=True,
        blank=True,
    )
    active = ActiveAccountManager()
    all_objects = models.Manager()

    objects = active

    def __str__(self):
        return f"{self.account_code} - {self.name}"


class JournalEntry(AbsoluteBaseModel):
    date = models.DateField()
    description = models.TextField()
    reference = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    reversed_entry = models.OneToOneField(
        "self", null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.date} - {self.description}"


class Transaction(AbsoluteBaseModel):
    journal = models.ForeignKey(
        JournalEntry, related_name="transactions", on_delete=models.CASCADE
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_debit = models.BooleanField()  # True if debit, False if credit

    def __str__(self):
        type_ = "Dr" if self.is_debit else "Cr"
        return f"{type_} {self.amount} to {self.account}"
