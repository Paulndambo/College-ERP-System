from apps.accounting.models import JournalEntry, Transaction  
from django.utils import timezone

def create_journal_entry(description, reference, user, transactions):
    """
    Creates a balanced journal entry.

    Params:
        - description: str
        - reference: str (e.g. invoice, PO number)
        - user: request.user
        - transactions: list of dicts like:
            {
                "account": Account instance,
                "amount": Decimal,
                "is_debit": True/False
            }
    """

    journal = JournalEntry.objects.create(
        date=timezone.now().date(),
        description=description,
        reference=reference,
        created_by=user
    )

    total_debit = 0
    total_credit = 0

    for tx in transactions:
        Transaction.objects.create(
            journal=journal,
            account=tx["account"],
            amount=tx["amount"],
            is_debit=tx["is_debit"]
        )
        if tx["is_debit"]:
            total_debit += tx["amount"]
        else:
            total_credit += tx["amount"]

    if total_debit != total_credit:
        raise ValueError("Unbalanced journal entry: Debits and Credits must match")

    return journal

def reverse_journal_entry(entry, user):
    if entry.reversed_entry:
        raise ValueError("This journal has already been reversed.")

    reversed_entry = JournalEntry.objects.create(
        date=timezone.now().date(),
        description=f"REVERSAL: {entry.description}",
        reference=f"REV-{entry.reference}",
        created_by=user
    )

    for tx in entry.transactions.all():
        Transaction.objects.create(
            journal=reversed_entry,
            account=tx.account,
            amount=tx.amount,
            is_debit=not tx.is_debit
        )

    entry.reversed_entry = reversed_entry
    entry.save()
    return reversed_entry
