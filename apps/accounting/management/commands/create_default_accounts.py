from django.core.management.base import BaseCommand
from apps.accounting.models import Account, AccountType


class Command(BaseCommand):
    help = 'Create default accounting accounts'

    def handle(self, *args, **kwargs):
        defaults = [
            #  ASSETS
            {"account_code": "1000", "name": "Bank", "type": "Asset"},
            {"account_code": "1010", "name": "Cash", "type": "Asset"},
            {"account_code": "1100", "name": "Inventory", "type": "Asset"},
            {"account_code": "1200", "name": "Accounts Receivable", "type": "Asset"},  # student debts

            # LIABILITIES
            {"account_code": "2100", "name": "Accounts Payable", "type": "Liability"},
            {"account_code": "2200", "name": "Student Deposits", "type": "Liability"},  # if used

            # INCOME
            {"account_code": "4000", "name": "Tuition Revenue", "type": "Income"},
            {"account_code": "4100", "name": "Miscellaneous Income", "type": "Income"},
            {"account_code": "4200", "name": "Library Fines", "type": "Income"},  # optional

            # EXPENSES
            {"account_code": "5000", "name": "Salaries Expense", "type": "Expense"},
            {"account_code": "5100", "name": "Utilities Expense", "type": "Expense"},
            {"account_code": "5200", "name": "Repairs & Maintenance", "type": "Expense"},
            {"account_code": "5300", "name": "Office Supplies", "type": "Expense"},
        ]

        for acc in defaults:
            acc_type, _ = AccountType.objects.get_or_create(
                name=acc["type"],
                defaults={
                    "normal_balance": "debit" if acc["type"] in ["Asset", "Expense"] else "credit"
                }
            )

            Account.objects.get_or_create(
                account_code=acc["account_code"],
                defaults={
                    "name": acc["name"],
                    "account_type": acc_type,
                    "is_default": True
                }
            )

        self.stdout.write(self.style.SUCCESS("Core chart of accounts seeded"))
        self.stdout.write(self.style.SUCCESS("Default accounts created successfully"))