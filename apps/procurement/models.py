from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

from apps.core.models import AbsoluteBaseModel

from django.db.models import Sum, F, DecimalField, ExpressionWrapper

User = get_user_model()
DOCUMENT_TYPE_CHOICES = [
    ("certificate_of_incorporation", "Certificate of Incorporation"),
    ("proposal_document", "Proposal Document"),
    ("business_registration", "Business Registration"),
    ("tax_compliance", "Tax Compliance Certificate"),
    ("audited_financials", "Audited Financial Statements"),
    ("bank_statements", "Bank Statements"),
    ("tax_clearance", "Tax Clearance Certificate"),
    ("professional_license", "Professional License"),
    ("insurance_certificate", "Insurance Certificate"),
    ("company_profile", "Company Profile"),
    ("technical_proposal", "Technical Proposal"),
    ("financial_proposal", "Financial Proposal"),
    ("performance_bond", "Performance Bond"),
    ("bid_security", "Bid Security"),
    ("experience_certificates", "Experience Certificates"),
    ("quality_certificates", "Quality Certificates"),
    ("other", "Other"),
]

BUSINESS_TYPE_CHOICES = [
    ("individual", "Individual"),
    ("sole_proprietor", "Sole Proprietor"),
    ("partnership", "Partnership"),
    ("limited", "Limited Company"),
    ("ngo", "NGO"),
    ("government", "Government"),
    ("other", "Other"),
]


class Tender(AbsoluteBaseModel):
    status_choices = [
        ("open", "Open"),
        ("awarded", "Awarded"),
        ("cancelled", "Cancelled"),
    ]
    tender_document = models.FileField(
        upload_to="tender_docs/",
        null=True,
        blank=True,
        help_text="Upload tender details and terms document",
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField()
    start_date = models.DateField(
        null=True, blank=True, help_text="Expected start date of the tender execution"
    )
    end_date = models.DateField(
        null=True, blank=True, help_text="Expected end date of the tender execution"
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    status = models.CharField(max_length=20, choices=status_choices, default="open")
    projected_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="The projected cost for the tender",
    )
    actual_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="The actual awarded amount for the tender",
    )

    def __str__(self):
        return self.title


class Vendor(AbsoluteBaseModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("blacklisted", "Blacklisted"),
    ]

    vendor_no = models.CharField(max_length=20, unique=True, blank=True, null=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    contact_person = models.CharField(
        max_length=255, blank=True, help_text="Name of the main contact at the company"
    )
    contact_person_phone = models.CharField(max_length=20, blank=True)
    contact_person_email = models.EmailField(blank=True, null=True)

    company_registration_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Company Registration Number or Business Number",
    )

    tax_pin = models.CharField(
        max_length=100, blank=True, help_text="KRA PIN or equivalent"
    )

    business_type = models.CharField(
        max_length=50,
        choices=BUSINESS_TYPE_CHOICES,
        blank=True,
        null=True,
        help_text="Type of business",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    def save(self, *args, **kwargs):
        from apps.procurement.utils import generate_unique_vendor_no

        if not self.vendor_no:
            self.vendor_no = generate_unique_vendor_no()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class TenderApplication(AbsoluteBaseModel):
    tender = models.ForeignKey(
        Tender, on_delete=models.CASCADE, related_name="applications"
    )
    vendor_no = models.CharField(max_length=50, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    contact_person = models.CharField(max_length=255, blank=True, null=True)
    contact_person_phone = models.CharField(max_length=20, blank=True, null=True)
    contact_person_email = models.EmailField(blank=True, null=True)

    business_type = models.CharField(
        max_length=50,
        choices=BUSINESS_TYPE_CHOICES,
        blank=True,
        null=True,
        help_text="Type of business applying",
    )

    company_registration_number = models.CharField(
        max_length=100, blank=True, help_text="Business registration number"
    )

    tax_pin = models.CharField(
        max_length=100, blank=True, help_text="KRA PIN or equivalent"
    )

    status_choices = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("incomplete", "Incomplete"),
    ]
    status = models.CharField(
        max_length=20, choices=status_choices, default="incomplete"
    )
    reviewed_on = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_applications",
    )

    def __str__(self):
        return f"{self.company_name} - {self.tender.title}"


class ApplicationDocument(AbsoluteBaseModel):
    """Documents submitted with tender applications"""

    application = models.ForeignKey(
        TenderApplication, on_delete=models.CASCADE, related_name="documents"
    )

    document_name = models.CharField(max_length=255)
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
    )
    file = models.FileField(upload_to="application_documents/")
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.application.company_name} - {self.document_name}"


class VendorDocument(AbsoluteBaseModel):
    """Documents for approved vendors (copied from application documents)"""

    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, related_name="documents"
    )

    document_name = models.CharField(max_length=255)
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
    )
    document_file = models.FileField(upload_to="vendor_documents/")
    description = models.TextField(blank=True)

    source_application = models.ForeignKey(
        TenderApplication,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Application this document was copied from",
    )

    def __str__(self):
        return f"{self.vendor.name} - {self.document_name}"


class TenderAward(AbsoluteBaseModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("terminated", "Terminated"),
        ("cancelled", "Cancelled"),
        ("revoked", "Revoked"),
    ]
    tender = models.ForeignKey(
        "Tender", on_delete=models.CASCADE, related_name="awards"
    )
    vendor = models.ForeignKey(
        "Vendor", on_delete=models.CASCADE, related_name="awarded_tenders"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    award_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="The final agreed amount for the award",
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Total amount paid to vendor for this award",
    )

    @property
    def balance_due(self):
        """Amount remaining to be paid"""
        return self.award_amount - self.amount_paid

    @property
    def payment_status(self):
        """Get payment status"""
        if self.amount_paid == 0:
            return "Unpaid"
        elif self.amount_paid >= self.award_amount:
            return "Fully Paid"
        else:
            return "Partially Paid"

    def __str__(self):
        return (
            f"{self.vendor.name} awarded '{self.tender.title}' for {self.award_amount}"
        )


class PurchaseOrder(AbsoluteBaseModel):
    order_no = models.CharField(max_length=20, unique=True, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("received", "Received"),
        ],
        default="pending",
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    @property
    def total_amount(self):
        total = self.items.aggregate(
            total=Sum(
                ExpressionWrapper(
                    F("quantity") * F("unit_price"), output_field=DecimalField()
                )
            )
        )["total"]
        return total or 0

    def __str__(self):
        return f"PO-{self.id} - {self.vendor.name}"


class PurchaseItem(AbsoluteBaseModel):
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="items"
    )
    description = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField()
    name = models.CharField(
        max_length=100, help_text="Short name of the item e.g., 'Office Desk'"
    )
    unit = models.ForeignKey(
        "inventory.UnitOfMeasure", on_delete=models.SET_NULL, null=True
    )

    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(
        "inventory.Category", on_delete=models.SET_NULL, null=True, blank=True
    )

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.description} - {self.quantity} @ {self.unit_price} each"


class GoodsReceived(AbsoluteBaseModel):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    remarks = models.TextField(blank=True, null=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Goods Received for {self.purchase_order.vendor.name} - PO-{self.purchase_order.id}"


class PurchaseItemReceipt(models.Model):
    purchase_item = models.ForeignKey(PurchaseItem, on_delete=models.CASCADE)
    goods_received = models.ForeignKey(GoodsReceived, on_delete=models.CASCADE)
    quantity_received = models.PositiveIntegerField()
    received_on = models.DateTimeField(auto_now_add=True)


class VendorPayment(AbsoluteBaseModel):
    PAYMENT_METHODS = [
        ("Cash", "Cash"),
        ("Bank", "Bank Transfer"),
        ("Mpesa", "Mpesa"),
        ("Cheque", "Cheque"),
    ]
    tender_award = models.ForeignKey(TenderAward, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    reference = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    @property
    def vendor(self):
        return self.tender_award.vendor

    def __str__(self):
        return f"Payment to {self.tender_award.vendor.name} - {self.amount} ({self.reference})"


class VendorPaymentStatement(AbsoluteBaseModel):
    """Track payment history and balance for tender awards"""

    STATEMENT_TYPES = [
        ("Award", "Award"),
        ("Payment", "Payment"),
    ]

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    tender_award = models.ForeignKey(TenderAward, on_delete=models.CASCADE)
    statement_type = models.CharField(max_length=20, choices=STATEMENT_TYPES)
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    description = models.CharField(max_length=255)
    payment_method = models.CharField(
        max_length=50, choices=VendorPayment.PAYMENT_METHODS, blank=True, null=True
    )

    def __str__(self):
        return f"{self.vendor.name} - {self.tender_award.tender.title} - {self.statement_type}"
