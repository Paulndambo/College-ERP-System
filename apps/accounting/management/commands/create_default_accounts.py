# from django.core.management.base import BaseCommand
# from apps.accounting.models import Account, AccountType


# class Command(BaseCommand):
#     help = 'Create core and suggested accounting accounts'

#     def handle(self, *args, **kwargs):
#         accounts_to_create = [
#             # --- ASSETS ---
#             {"account_code": "1000", "name": "Bank", "type": "Asset"},
#             {"account_code": "1010", "name": "Cash", "type": "Asset"},
#             {"account_code": "1100", "name": "Inventory", "type": "Asset"},
#             {"account_code": "1200", "name": "Accounts Receivable", "type": "Asset"},  # student debts

#             # --- LIABILITIES ---
#             {"account_code": "2100", "name": "Accounts Payable", "type": "Liability"},
#             {"account_code": "2200", "name": "Student Deposits", "type": "Liability"},
#             {"account_code": "2300", "name": "Unearned Revenue", "type": "Liability"},  # new

#             # --- INCOME ---
#             {"account_code": "4000", "name": "Tuition Revenue", "type": "Income"},
#             {"account_code": "4100", "name": "Miscellaneous Income", "type": "Income"},
#             {"account_code": "4200", "name": "Library Fines", "type": "Income"},
#             {"account_code": "4300", "name": "Scholarship Discounts", "type": "Income", "is_contra": True},  # contra income

#             # --- EXPENSES ---
#             {"account_code": "5000", "name": "Salaries Expense", "type": "Expense"},
#             {"account_code": "5100", "name": "Utilities Expense", "type": "Expense"},
#             {"account_code": "5200", "name": "Repairs & Maintenance", "type": "Expense"},
#             {"account_code": "5300", "name": "Office Supplies", "type": "Expense"},
#             {"account_code": "5400", "name": "Bad Debts Expense", "type": "Expense"},  # new
#             {"account_code": "5500", "name": "Financial Aid Expense", "type": "Expense"},  # new
#         ]

#         for acc in accounts_to_create:
#             account_type, _ = AccountType.objects.get_or_create(
#                 name=acc["type"],
#                 defaults={
#                     "normal_balance": "debit" if acc["type"] in ["Asset", "Expense"] else "credit"
#                 }
#             )

#             account, created = Account.objects.get_or_create(
#                 account_code=acc["account_code"],
#                 defaults={
#                     "name": acc["name"],
#                     "account_type": account_type,
#                     "is_default": True,
#                     "is_contra": acc.get("is_contra", False)
#                 }
#             )

#             if created:
#                 self.stdout.write(self.style.SUCCESS(f"✔ Created account: {acc['name']} ({acc['account_code']})"))
#             else:
#                 self.stdout.write(self.style.NOTICE(f"ℹ Account already exists: {acc['name']} ({acc['account_code']})"))

#         self.stdout.write(self.style.SUCCESS("\n✅ Core + suggested accounts seeded successfully."))


from django.core.management.base import BaseCommand
from apps.accounting.models import AccountType, Account


class Command(BaseCommand):
    help = "Seed chart of accounts"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("🌱 Seeding account types and accounts...")
        )

        account_data = {
            "Asset": {
                "normal_balance": "debit",
                "accounts": [
                    {
                        "account_code": "1000",
                        "name": "Bank",
                        "cash_flow_section": "Operating",
                    },
                    {
                        "account_code": "1100",
                        "name": "Cash",
                        "cash_flow_section": "Operating",
                    },
                    {
                        "account_code": "1200",
                        "name": "Accounts Receivable",
                        "cash_flow_section": "Operating",
                    },
                ],
            },
            "Liability": {
                "normal_balance": "credit",
                "accounts": [
                    {
                        "account_code": "2000",
                        "name": "Accounts Payable",
                        "cash_flow_section": "Operating",
                    },
                ],
            },
            "Equity": {
                "normal_balance": "credit",
                "accounts": [
                    {
                        "account_code": "3000",
                        "name": "Owner’s Capital",
                        "cash_flow_section": "Financing",
                    },
                ],
            },
            "Income": {
                "normal_balance": "credit",
                "accounts": [
                    {
                        "account_code": "4000",
                        "name": "Sales Revenue",
                        "cash_flow_section": "Operating",
                    },
                    {
                        "account_code": "4100",
                        "name": "Tuition Revenue",
                        "cash_flow_section": "Operating",
                    },
                    {
                        "account_code": "4200",
                        "name": "Fines - Lost Books",
                        "cash_flow_section": "Operating",
                    },
                    {
                        "account_code": "4300",
                        "name": "Donor Contributions",
                        "cash_flow_section": "Financing",
                    },
                ],
            },
            "Expense": {
                "normal_balance": "debit",
                "accounts": [
                    {
                        "account_code": "5000",
                        "name": "Rent Expense",
                        "cash_flow_section": "Operating",
                    },
                    {
                        "account_code": "5100",
                        "name": "Scholarship Expense",
                        "cash_flow_section": "Operating",
                    },
                    {
                        "account_code": "5200",
                        "name": "Salaries & Wages",
                        "cash_flow_section": "Operating",
                    },
                    {
                        "account_code": "5400",
                        "name": "Office Supplies",
                        "cash_flow_section": "Operating",
                    },
                    {
                        "account_code": "5500",
                        "name": "Utilities",
                        "cash_flow_section": "Operating",
                    },
                    {
                        "account_code": "5600",
                        "name": "Repairs & Maintenance",
                        "cash_flow_section": "Operating",
                    },
                    {
                        "account_code": "5700",
                        "name": "Vendor Payments",
                        "cash_flow_section": "Operating",
                    },
                    {
                        "account_code": "5800",
                        "name": "Insurance Expense",
                        "cash_flow_section": "Operating",
                    },
                    {
                        "account_code": "5900",
                        "name": "Training & Development",
                        "cash_flow_section": "Operating",
                    },
                    {
                        "account_code": "5950",
                        "name": "Advertising & Promotion",
                        "cash_flow_section": "Operating",
                    },
                ],
            },
        }

        for type_name, acc_type_data in account_data.items():
            account_type, created_type = AccountType.all_objects.get_or_create(
                name=type_name,
                defaults={"normal_balance": acc_type_data["normal_balance"]},
            )

            if created_type:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Created account type: {type_name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"⏭️ Account type exists: {type_name}")
                )

            # Always ensure correct normal_balance
            if account_type.normal_balance != acc_type_data["normal_balance"]:
                account_type.normal_balance = acc_type_data["normal_balance"]
                account_type.save()

            for acc_data in acc_type_data["accounts"]:
                account, created = Account.all_objects.get_or_create(
                    account_code=acc_data["account_code"],
                    defaults={
                        "name": acc_data["name"],
                        "account_type": account_type,
                        "normal_balance": account_type.normal_balance,
                        "cash_flow_section": acc_data["cash_flow_section"],
                    },
                )

                if not created:
                    updated = False
                    if account.cash_flow_section != acc_data["cash_flow_section"]:
                        account.cash_flow_section = acc_data["cash_flow_section"]
                        updated = True
                    if account.account_type != account_type:
                        account.account_type = account_type
                        updated = True
                    if account.normal_balance != account_type.normal_balance:
                        account.normal_balance = account_type.normal_balance
                        updated = True
                    if updated:
                        account.save()

                status = "✅ Created" if created else "⏭️ Exists"
                self.stdout.write(
                    self.style.SUCCESS(
                        f"   {status}: {acc_data['name']} ({acc_data['account_code']})"
                    )
                )

        self.stdout.write(self.style.SUCCESS("🎉 Chart of accounts seeding complete."))
