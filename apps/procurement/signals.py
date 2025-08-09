import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.procurement.models import (
    GoodsReceived,
    TenderAward,
    VendorPayment,
    VendorPaymentStatement,
)
from apps.accounting.services.journals import create_journal_entry
from apps.accounting.models import Account

logger = logging.getLogger(__name__)

from decimal import Decimal


@receiver(post_save, sender=VendorPayment)
def create_vendor_payment_journal_entry(sender, instance, created, **kwargs):
    """
    Create journal entry when a vendor payment is created
    """
    if not created:
        return

    try:
        expense_account = Account.objects.get(name__iexact="Vendor Payments")

        payment_method = instance.payment_method.strip().lower()

        print("********This part was reached**************")

        if payment_method == "cash":
            cash_account = Account.objects.get(name__iexact="Cash")
        else:
            cash_account = Account.objects.get(name__iexact="Bank")

        logger.info(f"expense_account {expense_account}")
        logger.info(f"payment_method {payment_method}")
        logger.info(f"cash_account {cash_account}")
        logger.info(f"payment_method {payment_method}")

        create_journal_entry(
            description=instance.description,
            reference=f"VP-{instance.id}",
            user=instance.paid_by,
            transactions=[
                {
                    "account": expense_account,
                    "amount": instance.amount,
                    "is_debit": True,
                },
                {"account": cash_account, "amount": instance.amount, "is_debit": False},
            ],
        )

        logger.info(f"Journal entry created for vendor payment {instance.id}")

    except Account.DoesNotExist as e:
        logger.error(f"Missing account for vendor payment journal entry: {e}")
    except Exception as e:
        logger.error(
            f"Failed to create journal entry for vendor payment {instance.id}: {e}"
        )


@receiver(post_save, sender=TenderAward)
def create_initial_vendor_statement(sender, instance, created, **kwargs):
    """
    Create initial vendor payment statement when tender is awarded
    """
    if not created:
        return

    try:
        # Create initial statement showing the full award amount as balance
        VendorPaymentStatement.objects.create(
            vendor=instance.vendor,
            tender_award=instance,
            statement_type="Award",
            debit=instance.award_amount,
            balance=instance.award_amount,
            description=f"Award - {instance.tender.title}",
        )
        logger.info(f"Initial statement created for tender award {instance.id}")

    except Exception as e:
        logger.error(
            f"Failed to create initial statement for tender award {instance.id}: {e}"
        )


# @receiver(post_save, sender=TenderAward)
# def create_tender_approval_journal(sender, instance, created, **kwargs):
#     print("Signal triggered for TenderAward")
#     if not instance.award_amount or instance.status.lower() != "active":
#         return

#     try:
#         expense_account = Account.objects.get(name="Vendor Payments")
#         payable_account = Account.objects.get(name="Accounts Payable")

#         create_journal_entry(
#             description=f"Tender awarded to vendor {instance.vendor.name}",
#             reference=f"TENDER-{instance.tender.id}",
#             user=instance.created_by,
#             transactions=[
#                 {"account": expense_account, "amount": instance.award_amount, "is_debit": True},
#                 {"account": payable_account, "amount": instance.award_amount, "is_debit": False},
#             ],
#         )
#     except Account.DoesNotExist as e:
#         print(f"Missing account for journal entry: {e}")
