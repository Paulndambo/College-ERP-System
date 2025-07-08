
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.finance.models import LibraryFinePayment
from apps.procurement.models import GoodsReceived, VendorPayment
from apps.accounting.services.journals import create_journal_entry
from apps.accounting.models import Account
from apps.student_finance.models import StudentFeePayment

@receiver(post_save, sender=GoodsReceived)
def create_goods_received_journal(sender, instance, created, **kwargs):
    if not created:
        return

    po = instance.purchase_order
    total = sum(item.quantity * item.unit_price for item in po.items.all())

    inventory = Account.objects.get(name="Inventory", is_default=True)
    payable = Account.objects.get(name="Accounts Payable", is_default=True)

    create_journal_entry(
        description=f"Goods received for PO-{po.id}",
        reference=f"PO-{po.id}",
        user=po.created_by,
        transactions=[
            {"account": inventory, "amount": total, "is_debit": True},
            {"account": payable, "amount": total, "is_debit": False}
        ]
    )

@receiver(post_save, sender=VendorPayment)
def create_vendor_payment_journal(sender, instance, created, **kwargs):
    if not created:
        return

    payable = Account.objects.get(name="Accounts Payable", is_default=True)
    bank = Account.objects.get(name="Bank", is_default=True)

    create_journal_entry(
        description=f"Payment to vendor {instance.vendor.name}",
        reference=instance.reference,
        user=instance.paid_by,
        transactions=[
            {"account": payable, "amount": instance.amount, "is_debit": True},
            {"account": bank, "amount": instance.amount, "is_debit": False}
        ]
    )


@receiver(post_save, sender=StudentFeePayment)
def create_fee_payment_journal(sender, instance, created, **kwargs):
    if not created:
        return

    bank = Account.objects.get(name="Bank", is_default=True)
    tuition = Account.objects.get(name="Tuition Revenue")  # Add this account if not present

    create_journal_entry(
        description=f"Fee payment by {instance.student.full_name}",
        reference=f"FEEPAY-{instance.id}",
        user=instance.created_by,
        transactions=[
            {"account": bank, "amount": instance.amount, "is_debit": True},   # Asset ↑
            {"account": tuition, "amount": instance.amount, "is_debit": False} # Income ↑
        ]
    )


@receiver(post_save, sender=LibraryFinePayment)
def create_book_fine_journal(sender, instance, created, **kwargs):
    if not created:
        return

    bank = Account.objects.get(name="Bank", is_default=True)
    fines = Account.objects.get(name="Miscellaneous Income")  

    create_journal_entry(
        description=f"Lost book fine paid by {instance.student.full_name}",
        reference=f"BOOKFINE-{instance.id}",
        user=instance.created_by,
        transactions=[
            {"account": bank, "amount": instance.amount, "is_debit": True},   # Asset ↑
            {"account": fines, "amount": instance.amount, "is_debit": False} # Income ↑
        ]
    )