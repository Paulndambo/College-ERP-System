import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.finance.models import LibraryFinePayment
from apps.inventory.models import InventoryItem
from apps.payroll.models import SalaryPayment
from apps.procurement.models import GoodsReceived, VendorPayment
from apps.accounting.services.journals import create_journal_entry
from apps.accounting.models import Account
from apps.student_finance.models import StudentFeeInvoice, StudentFeePayment



logger = logging.getLogger(__name__)



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
            {"account": payable, "amount": total, "is_debit": False},
        ],
    )


@receiver(post_save, sender=GoodsReceived)
def update_po_status(sender, instance, created, **kwargs):
    if created:
        po = instance.purchase_order
        po.status = "received"
        po.save()


@receiver(post_save, sender=StudentFeePayment)
def create_fee_payment_journal(sender, instance, created, **kwargs):
    
    if not created:
        return

    tuition = Account.objects.get(name="Tuition Revenue")

    if instance.payment_method == "Cash":
        receiving_account = Account.objects.get(name="Cash")
    elif instance.payment_method == "Bank":
        receiving_account = Account.objects.get(name="Bank")
    else:
        receiving_account = Account.objects.get(
            name="Other Receipts"
        )  # Fallback or M-Pesa
    full_name = instance.student.user.first_name + " " + instance.student.user.last_name
    create_journal_entry(
        description=f"Fee payment by {full_name} via {instance.payment_method}",
        reference=f"FEEPAY-{instance.id}",
        user=instance.created_by,  # Ensure this is present
        transactions=[
            {
                "account": receiving_account,
                "amount": instance.amount,
                "is_debit": True,
            },  # Asset ↑
            {
                "account": tuition,
                "amount": instance.amount,
                "is_debit": False,
            },  # Revenue ↑
        ],
    )


@receiver(post_save, sender=StudentFeeInvoice)
def create_invoice_journal_entry(sender, instance, created, **kwargs):
    logger.info(f"Creating journal entry for invoice {instance.id} - created: {created}")
    if not created:
        return

    try:
        receivable = Account.objects.get(name="Accounts Receivable", is_default=True)
        tuition = Account.objects.get(name="Tuition Revenue")
        full_name = (
            instance.student.user.first_name + " " + instance.student.user.last_name
        )
        create_journal_entry(
            description=f"Invoicing for {full_name}",
            reference=f"INVOICE-{instance.id}",
            user=instance.created_by,
            transactions=[
                {"account": receivable, "amount": instance.amount, "is_debit": True},
                {"account": tuition, "amount": instance.amount, "is_debit": False},
            ],
        )
    except Account.DoesNotExist as e:
        print(f"Account missing for journal entry: {e}")


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
            {"account": bank, "amount": instance.amount, "is_debit": True},  # Asset ↑
            {
                "account": fines,
                "amount": instance.amount,
                "is_debit": False,
            },  # Income ↑
        ],
    )


@receiver(post_save, sender=SalaryPayment)
def create_salary_payment_journal(sender, instance, created, **kwargs):
    """
    Create a journal entry automatically when a salary payment is completed.
    """
    # Only create if payment is completed and no journal entry already linked
    if instance.payment_status != "completed" or getattr(
        instance, "journal_entry", None
    ):
        return

    # Skip invalid or zero payments
    if not instance.amount_paid or instance.amount_paid <= 0:
        logger.warning(
            f"[SalaryPayment:{instance.id}] Invalid amount: {instance.amount_paid}"
        )
        return

    try:
        # Get Salaries & Wages expense account by NAME
        salaries_wages_acc = Account.objects.get(name__iexact="Salaries & Wages")

        # Map payment method to account NAME
        payment_account_map = {
            "bank": lambda: Account.objects.get(code="1000"),  # Bank account by code
            "cash": lambda: Account.objects.get(
                name__iexact="Cash"
            ),  # Cash account by name
            "mpesa": lambda: Account.objects.get(code="1020"),  # M-Pesa account by code
            "cheque": lambda: Account.objects.get(code="1000"),  # Cheque paid from bank
        }

        # Default to Cash if method not in map
        account_getter = payment_account_map.get(
            instance.payment_method, lambda: Account.objects.get(name__iexact="Cash")
        )
        cash_account = account_getter()

        logger.info(
            f"[SalaryPayment:{instance.id}] Accounts found: {salaries_wages_acc.name}, {cash_account.name}"
        )

    except Account.DoesNotExist as e:
        logger.error(f"[SalaryPayment:{instance.id}] Required accounts not found: {e}")
        return

    try:
        # Create the journal entry
        journal_entry = create_journal_entry(
            description=f"Salary Payment - {instance.payslip.staff.user.first_name} {instance.payslip.staff.user.last_name} ({instance.payslip.payroll_period_start.strftime('%b %Y')})",
            reference=f"SAL-PAY-{instance.id}",
            user=instance.processed_by,
            transactions=[
                {
                    "account": salaries_wages_acc,
                    "amount": instance.amount_paid,
                    "is_debit": True,
                },
                {
                    "account": cash_account,
                    "amount": instance.amount_paid,
                    "is_debit": False,
                },
            ],
        )

        # Link payment to journal entry (ForeignKey allows multiple payments to same journal)
        SalaryPayment.objects.filter(pk=instance.pk).update(journal_entry=journal_entry)
        logger.info(
            f"[SalaryPayment:{instance.id}] Journal entry created successfully: {journal_entry.id}"
        )

    except Exception as e:
        logger.error(f"[SalaryPayment:{instance.id}] Error creating journal entry: {e}")
