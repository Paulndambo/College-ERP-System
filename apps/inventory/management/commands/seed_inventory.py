from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random

from apps.inventory.models import Category, InventoryItem, StockReceipt, StockIssue
from apps.procurement.models import Vendor, PurchaseOrder, PurchaseItem
from apps.schools.models import Department
from django.contrib.auth import get_user_model

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = "Seed inventory items, stock receipts, and issues using existing vendors"

    def handle(self, *args, **kwargs):
        # Get admin user
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
        )

        departments = list(Department.objects.filter(department_type="Not Academic"))
        if not departments:
            self.stdout.write(self.style.ERROR("Please seed departments first using `seed_departments`."))
            return

        vendors = list(Vendor.objects.all())
        if not vendors:
            self.stdout.write(self.style.ERROR("No vendors found. Run the tender seeder first."))
            return

        # Categories
        categories_data = [
            ("Furniture", "Chairs, desks, and tables"),
            ("Books", "Textbooks and reference materials"),
            ("Stationery", "Office and school supplies"),
        ]

        categories = []
        for name, desc in categories_data:
            cat, _ = Category.objects.get_or_create(name=name, defaults={"description": desc})
            categories.append(cat)
            self.stdout.write(self.style.SUCCESS(f"✔ Category: {cat.name}"))

        # Inventory items
        items_data = [
            ("Office Desk", "Wooden desk", "Furniture", "pcs"),
            ("Introduction to Economics", "Textbook for business dept", "Books", "books"),
            ("Ballpoint Pens", "Blue pens for exams", "Stationery", "dozens"),
        ]

        inventory_items = []
        for name, desc, cat_name, unit in items_data:
            category = next((c for c in categories if c.name == cat_name), None)
            item = InventoryItem.objects.create(
                name=name,
                description=desc,
                category=category,
                unit=unit,
                quantity_in_stock=0
            )
            inventory_items.append(item)
            self.stdout.write(self.style.SUCCESS(f"Created Inventory Item: {item.name}"))

        # Purchase orders + StockReceipt
        for item in inventory_items:
            vendor = random.choice(vendors)
            po = PurchaseOrder.objects.create(vendor=vendor, created_by=admin, status="approved")
            quantity = random.randint(10, 50)

            PurchaseItem.objects.create(
                purchase_order=po,
                name=item.name,
                description=item.description,
                quantity=quantity,
                unit=item.unit,
                unit_price=random.randint(100, 5000),
                category=item.category  # link back to same category
            )

            StockReceipt.objects.create(
                inventory_item=item,
                purchase_order=po,
                vendor=vendor,
                quantity_received=quantity,
                remarks="Initial batch"
            )

            self.stdout.write(self.style.SUCCESS(f"Received {quantity} {item.unit} of {item.name} from {vendor.name}"))

        # Stock Issues
        for item in inventory_items:
            dept = random.choice(departments)
            qty = random.randint(1, 10)
            if item.quantity_in_stock >= qty:
                StockIssue.objects.create(
                    inventory_item=item,
                    quantity=qty,
                    issued_to=dept,
                    issued_by=admin,
                    remarks=f"Issued to {dept.name}"
                )
                self.stdout.write(self.style.SUCCESS(f"Issued {qty} {item.unit} of {item.name} to {dept.name}"))

        self.stdout.write(self.style.SUCCESS("Inventory seeding complete."))
