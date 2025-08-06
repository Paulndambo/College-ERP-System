
from django.db.models import Max
from datetime import datetime
from django.utils.timezone import now
from apps.procurement.models import PurchaseOrder


def generate_unique_vendor_no(prefix="VND", padding=5):
    from apps.procurement.models import Vendor
    year = datetime.now().year
    last_vendor = Vendor.objects.filter(vendor_no__startswith=f"{prefix}-{year}").count()
    return f"{prefix}-{year}-{str(last_vendor + 1).zfill(padding)}"


def generate_payment_reference():
    from apps.procurement.models import VendorPayment
    last_payment = VendorPayment.objects.order_by("-id").first()
    count = last_payment.id + 1 if last_payment else 1
    return f"V-payment-{str(count).zfill(3)}"

def generate_order_no(prefix="PO", padding=5):
    year = now().year
    count = PurchaseOrder.objects.filter(order_no__startswith=f"{prefix}-{year}").count()
    return f"{prefix}-{year}-{str(count + 1).zfill(padding)}"