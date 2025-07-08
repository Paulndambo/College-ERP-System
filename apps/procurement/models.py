
from django.db import models
from django.contrib.auth import get_user_model

from apps.core.models import AbsoluteBaseModel

User = get_user_model()


class Tender(AbsoluteBaseModel):
    status_choices = [
    ("open", "Open"),
    ("awarded", "Awarded"),
]

    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    status = models.CharField(max_length=20, choices=status_choices, default="open")
    projected_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, help_text="The projected cost for the tender"
    )
    actual_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, help_text="The actual awarded amount for the tender"
    )
    def __str__(self):
        return self.title


class TenderApplication(AbsoluteBaseModel):
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="applications")
    
    company_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    
    status_choices = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default="pending")
    reviewed_on = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_applications")

    def __str__(self):
        return f"{self.company_name} - {self.tender.title}"

    def convert_to_vendor(self):
        from apps.procurement.models import Vendor, TenderAward

        # Create or get the vendor
        vendor, created = Vendor.objects.get_or_create(
            name=self.company_name,
            defaults={
                "email": self.email,
                "phone": self.phone,
                "address": self.address,
            }
        )

        self.vendor = vendor
        self.save()

        # Only create a TenderAward if one doesn't already exist for the tender
        if not TenderAward.objects.filter(tender=self.tender).exists():
            # Determine the award amount (this can be the tender's projected amount or some other logic)
            award_amount = self.tender.projected_amount  # Example: set award amount equal to projected_amount

            TenderAward.objects.create(
                tender=self.tender,
                vendor=vendor,
                award_amount=award_amount
            )

            # Update the tender's actual amount (this will be set once awarded)
            self.tender.actual_amount = award_amount
            self.tender.status = "awarded"
            self.tender.save()

        return vendor



class Vendor(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
   

    def __str__(self):
        return self.name


class TenderAward(AbsoluteBaseModel):
    tender = models.OneToOneField('Tender', on_delete=models.CASCADE, related_name='award')
    vendor = models.ForeignKey('Vendor', on_delete=models.CASCADE, related_name='awarded_tenders')
    
    award_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00, help_text="The final agreed amount for the award"
    )

    def __str__(self):
        return f"{self.vendor.name} awarded '{self.tender.title}' for {self.award_amount}"


class PurchaseOrder(AbsoluteBaseModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("received", "Received")
    ], default="pending")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"PO-{self.id} - {self.vendor.name}"


class PurchaseItem(AbsoluteBaseModel):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    description = models.CharField(max_length=255)
    quantity = models.IntegerField()
    name = models.CharField(max_length=100, help_text="Short name of the item e.g., 'Office Desk'")
    unit = models.CharField(max_length=50, help_text="Unit of measure, e.g., pcs, reams, litres")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey('inventory.Category', on_delete=models.SET_NULL, null=True, blank=True)
    @property
    def total_price(self):
        return self.quantity * self.unit_price
    def __str__(self):
        return f"{self.description} - {self.quantity} @ {self.unit_price} each"

class GoodsReceived(AbsoluteBaseModel):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    remarks = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Goods Received for {self.purchase_order.vendor.name} - PO-{self.purchase_order.id}"


class VendorPayment(AbsoluteBaseModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=50)
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"Payment to {self.vendor.name} - {self.amount} ({self.reference})"