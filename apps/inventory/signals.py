from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.inventory.models import StockReceipt, StockIssue, InventoryItem, Category
from apps.procurement.models import GoodsReceived, PurchaseItem


# Update stock when a StockReceipt is created manually
@receiver(post_save, sender=StockReceipt)
def increase_stock_on_receipt(sender, instance, created, **kwargs):
    if created:
        item = instance.inventory_item
        item.quantity_in_stock += instance.quantity_received
        item.save()


# Update stock when a StockIssue is created
@receiver(post_save, sender=StockIssue)
def decrease_stock_on_issue(sender, instance, created, **kwargs):
    if created:
        item = instance.inventory_item
        item.quantity_in_stock = max(0, item.quantity_in_stock - instance.quantity)
        item.save()


# Sync PurchaseItems to Inventory and update stock when GoodsReceived is created
@receiver(post_save, sender=GoodsReceived)
def sync_inventory_on_goods_received(sender, instance, created, **kwargs):
    if not created:
        return

    purchase_order = instance.purchase_order
    vendor = purchase_order.vendor

    # Get or create default category
    default_category, _ = Category.objects.get_or_create(
        name="Uncategorized",
        defaults={"description": "Default category for unspecified items"}
    )

    for item in purchase_order.items.all():
        category = item.category
        # Create or get the inventory item
        inventory_item, _ = InventoryItem.objects.get_or_create(
            name=item.name,
            defaults={
                'description': item.description,
                'unit': item.unit,
                'category': category
            }
        )

        # Increase inventory quantity
        inventory_item.quantity_in_stock += item.quantity
        inventory_item.save()

        # Log a StockReceipt for transparency
        StockReceipt.objects.create(
            inventory_item=inventory_item,
            purchase_order=purchase_order,
            vendor=vendor,
            quantity_received=item.quantity,
            remarks=f"Auto-created from GoodsReceived PO-{purchase_order.id}"
        )
