from datetime import datetime


def generate_payment_reference(staff_no, prefix="SAL"):
    """
    Generate a payment reference using prefix, date, and staff number.
    Example: SAL-20250809-EMP001
    """
    date_str = datetime.now().strftime("%Y%m%d")
    clean_staff_no = str(staff_no).replace(" ", "").upper()
    return f"{prefix}-{date_str}-{clean_staff_no}"
