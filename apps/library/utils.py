from .models import BorrowTransaction


from datetime import date, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError

from .models import BorrowTransaction


class LibraryCalculations:
    @staticmethod
    def get_default_borrow_days(member):
        config_rules = member.library_config.rules.filter(rule_type="Borrow")
        rule = next(
            (r for r in config_rules if member.role.lower() in r.name.lower()), None
        )
        return rule.integer if rule and rule.integer else 14

    @staticmethod
    def get_max_renewals(member):
        config_rules = member.library_config.rules.filter(rule_type="Borrow")
        rule = next(
            (
                r
                for r in config_rules
                if "max renewals" in r.name.lower()
                and member.role.lower() in r.name.lower()
            ),
            None,
        )
        return rule.integer if rule and rule.integer is not None else 2

    @staticmethod
    def get_fine_per_day(member):
        config_rules = member.library_config.rules.filter(rule_type="Fine")
        rule = next(
            (r for r in config_rules if member.role.lower() in r.name.lower()), None
        )
        return rule.decimal if rule and rule.decimal is not None else Decimal("0.50")

    @staticmethod
    def calculate_overdue_days(borrow_transaction: BorrowTransaction):
        if not borrow_transaction.due_date:
            return 0
        end_date = borrow_transaction.return_date or date.today()
        overdue_days = (end_date - borrow_transaction.due_date).days
        return max(overdue_days, 0)

    @staticmethod
    def calculate_fine(borrow_transaction: BorrowTransaction):
        overdue_days = LibraryCalculations.calculate_overdue_days(borrow_transaction)
        member = borrow_transaction.member
        fine_per_day = LibraryCalculations.get_fine_per_day(member)
        total_fine = Decimal(overdue_days) * fine_per_day

        if borrow_transaction.status == "Lost":
            total_fine += borrow_transaction.book.unit_price

        return total_fine

    @staticmethod
    def calculate_due_date(borrow_transaction: BorrowTransaction):
        member = borrow_transaction.member
        default_days = LibraryCalculations.get_default_borrow_days(member)
        return borrow_transaction.borrow_date + timedelta(days=default_days)

    @staticmethod
    def renew_borrow_transaction(borrow_transaction: BorrowTransaction):
        if borrow_transaction.status != "Pending Return":
            raise ValidationError("Only active borrow transactions can be renewed.")

        max_renewals = LibraryCalculations.get_max_renewals(borrow_transaction.member)
        if borrow_transaction.renewal_count >= max_renewals:
            raise ValidationError(
                "Maximum renewals reached for this borrow transaction."
            )

        borrow_transaction.renewal_count += 1

        default_days = LibraryCalculations.get_default_borrow_days(
            borrow_transaction.member
        )
        borrow_transaction.due_date += timedelta(days=default_days)

        borrow_transaction.save()
        return borrow_transaction


def generate_copy_number(book, status="Pending Return"):
    """
    Generate the next available copy number for a given book.

    Args:
        book: Book instance
        status: Filter borrowed copies by status (default: "Pending Return")

    Returns:
        A string like 'ISBN-001' or 'B<book_id>-001', or None if all copies are borrowed.
    """
    borrowed_copies = BorrowTransaction.objects.filter(
        book=book, status=status
    ).values_list("copy_number", flat=True)

    for i in range(1, book.total_copies + 1):
        copy_number = f"{book.isbn or f'B{book.id}'}-{i:03d}"
        if copy_number not in borrowed_copies:
            return copy_number

    return None
