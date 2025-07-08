from rest_framework import generics

from apps.accounting.models import Account
from apps.accounting.services.journals import create_journal_entry
from .models import Vendor, PurchaseOrder, GoodsReceived, VendorPayment
from .serializers import (
    VendorSerializer,
    PurchaseOrderSerializer,
    GoodsReceivedSerializer,
    VendorPaymentSerializer
)


class VendorListCreateView(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer


class PurchaseOrderListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class GoodsReceivedCreateView(generics.CreateAPIView):
    queryset = GoodsReceived.objects.all()
    serializer_class = GoodsReceivedSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        po = instance.purchase_order
        po.status = "received"
        po.save()

        # Trigger accounting entry here:
        # Debit Inventory (Asset)
        # Credit Accounts Payable (Liability)
        # Calculate total value of goods received
        # Assuming each item in the PO has a quantity and unit_price
        total = sum([item.quantity * item.unit_price for item in po.items.all()])

        inventory_account = Account.objects.get(name="Inventory")
        payable_account = Account.objects.get(name="Accounts Payable")

        create_journal_entry(
            description=f"Goods received for PO-{po.id} from {po.vendor.name}",
            reference=f"PO-{po.id}",
            user=self.request.user,
            transactions=[
                {"account": inventory_account, "amount": total, "is_debit": True},   # Asset ↑
                {"account": payable_account, "amount": total, "is_debit": False}     # Liability ↑
            ]
        )

class VendorPaymentListCreateView(generics.ListCreateAPIView):
    queryset = VendorPayment.objects.all()
    serializer_class = VendorPaymentSerializer

    def perform_create(self, serializer):
        instance = serializer.save(paid_by=self.request.user)

        # Trigger journal entry:
        # Debit Accounts Payable (Liability ↓)
        # Credit Bank (Asset ↓)
        payable_account = Account.objects.get(name="Accounts Payable")
        bank_account = Account.objects.get(name="Bank")

        create_journal_entry(
            description=f"Vendor payment to {instance.vendor.name}",
            reference=instance.reference,
            user=self.request.user,
            transactions=[
                {"account": payable_account, "amount": instance.amount, "is_debit": True},   # Liability ↓
                {"account": bank_account, "amount": instance.amount, "is_debit": False}      # Asset ↓
            ]
        )
