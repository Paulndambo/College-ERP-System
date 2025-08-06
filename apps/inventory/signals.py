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



@receiver(post_save, sender=GoodsReceived)
def sync_inventory_on_goods_received(sender, instance, created, **kwargs):
    if not created:
        return

    purchase_order = instance.purchase_order
    vendor = purchase_order.vendor

    # Get or create default category
    default_category, _ = Category.objects.get_or_create(
        name="Uncategorized",
        defaults={"description": "Default category for unspecified items"},
    )

    for item in purchase_order.items.all():
        category = item.category or default_category

        inventory_item, created = InventoryItem.objects.get_or_create(
            name=item.name,
            category=category,
            defaults={
                "description": item.description,
                "unit": item.unit,
                "category": category,
                "unit_valuation": item.unit_price,
                "quantity_in_stock": item.quantity,
                # For fixed assets or custom logic:
                "total_valuation": item.unit_price * item.quantity,
            },
        )

        if not created:
           
            existing_qty = inventory_item.quantity_in_stock
            existing_total_value = (inventory_item.unit_valuation or 0) * existing_qty

           
            new_qty = item.quantity
            new_value = item.unit_price * new_qty

            combined_qty = existing_qty + new_qty
            combined_total_value = existing_total_value + new_value

            inventory_item.quantity_in_stock = combined_qty
            inventory_item.unit_valuation = (
                combined_total_value / combined_qty if combined_qty else item.unit_price
            )
            inventory_item.total_valuation = combined_total_value  # Optional, for fixed asset style use
            inventory_item.save()

        # Log a StockReceipt for transparency
        StockReceipt.objects.create(
            inventory_item=inventory_item,
            purchase_order=purchase_order,
            vendor=vendor,
            quantity_received=item.quantity,
            remarks=f"Auto-created from GoodsReceived PO-{purchase_order.id}",
        )


# Sync PurchaseItems to Inventory and update stock when GoodsReceived is created
# @receiver(post_save, sender=GoodsReceived)
# def sync_inventory_on_goods_received(sender, instance, created, **kwargs):
#     if not created:
#         return

#     purchase_order = instance.purchase_order
#     vendor = purchase_order.vendor

#     # Get or create default category
#     default_category, _ = Category.objects.get_or_create(
#         name="Uncategorized",
#         defaults={"description": "Default category for unspecified items"},
#     )

#     for item in purchase_order.items.all():
#         category = item.category
#         # Create or get the inventory item
#         inventory_item, _ = InventoryItem.objects.get_or_create(
#             name=item.name,
#             category=category,
#             defaults={
#                 "description": item.description,
#                 "unit": item.unit,
#                 "category": category,
#                 "valuation": item.unit_price * item.quantity
#             },
#         )

#         # Increase inventory quantity
#         inventory_item.quantity_in_stock += item.quantity
#         inventory_item.save()

#         # Log a StockReceipt for transparency
#         StockReceipt.objects.create(
#             inventory_item=inventory_item,
#             purchase_order=purchase_order,
#             vendor=vendor,
#             quantity_received=item.quantity,
#             remarks=f"Auto-created from GoodsReceived PO-{purchase_order.id}",
#         )
