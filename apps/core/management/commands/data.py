# permissions/management/commands/seed_modules.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.core.models import Module

# List uses (group_title, menu_label) so we can disambiguate duplicates
MODULES = [
    ("", "Dashboard"),
    ("Academics", "Campuses"),
    ("Academics", "Schools"),
    ("Academics", "Departments"),
    ("Academics", "Programmes"),
    ("Academics", "Units"),
    ("Academics", "Cohorts"),
    ("Academics", "Sessions"),
    ("Academics", "Semesters"),
    ("Academics", "Academic Years"),
    ("Students", "Students"),
    ("Students", "Admissions"),
    ("Students", "Marks"),
    ("Students", "Assessment List"),
    ("Students", "Transcripts"),
    ("Staff & HR", "All Staff"),
    ("Staff & HR", "Positions"),
    ("Staff & HR", "Leave Entitlements"),
    ("Staff & HR", "Leave Applications"),
    ("Staff & HR", "Leaves"),
    ("Finance", "Fee Invoices"),
    ("Finance", "Fee Statements"),
    ("Finance", "Fee Structure"),
    ("Finance", "Fee Payments"),
    ("Finance", "Library Payments"),
    ("Payroll", "Payroll"),
    ("Payroll", "Payslips"),
    ("Payroll", "Overtime Payments"),
    ("Library", "Books"),
    ("Library", "Members"),
    ("Library", "Borrowed Books"),
    ("Library", "Fines"),
    ("Hostel", "Bookings"),
    ("Hostel", "Rooms"),
    ("Procurement", "Orders"),
    ("Procurement", "Vendors"),
    ("Procurement", "Tenders"),
    ("Procurement", "Tender Applications"),
    ("Procurement", "Awarded Tenders"),
    ("Procurement", "Tender Payments"),
    ("Inventory", "Store"),
    ("Accounts", "Chart of Accounts"),
    ("Accounts", "Account Types"),
    ("Accounts", "Transactions"),
    ("Accounts", "Reports"),
    ("Archived", "Accounts"),
    ("Archived", "Account Types"),
    ("Settings", "Settings"),
]


class Command(BaseCommand):
    help = "Seed initial modules into the Module table (based on sidebar titles)"

    def handle(self, *args, **kwargs):
        created_count = 0
        updated_count = 0

        for group, label in MODULES:
            # code is stable and unique: group + label slugified, use underscores
            base = f"{group} {label}" if group else label
            code = slugify(base).replace("-", "_")
            name = label  # keep the display name exactly as the menu label

            obj, created = Module.objects.update_or_create(
                code=code, defaults={"name": name}
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created module: {name} (code: {code})")
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f"Updated/exists: {name} (code: {code})")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created: {created_count}, Updated/Existing: {updated_count}."
            )
        )
