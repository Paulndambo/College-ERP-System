import random
from datetime import datetime


def payment_ref_generator(
    suffix: str = "FPT", length: int = 3, model=None, field: str = "reference"
) -> str:
    """
    Generate a unique reference for invoices or receipts.

    Format: YYMMDD + random digits + optional suffix
    Example: 250824482INV

    Args:
        suffix (str): Optional suffix (e.g. "INV", "RCP")
        length (int): Number of random digits
        model (Model): Django model to check uniqueness against
        field (str): Field name on the model that must be unique
    """
    date_str = datetime.now().strftime("%y%m%d")

    while True:
        rand = str(
            random.randint(10 ** (length - 1), (10**length) - 1)
        )  # e.g. 3 digits → 100–999
        ref = f"{date_str}{rand}{suffix}" if suffix else f"{date_str}{rand}"

        if model:
            # check if already exists in DB
            if not model.objects.filter(**{field: ref}).exists():
                return ref
        else:
            return ref
