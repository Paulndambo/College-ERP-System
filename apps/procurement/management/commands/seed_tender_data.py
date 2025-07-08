
# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from django.contrib.auth import get_user_model
# from faker import Faker
# import random
# from datetime import timedelta

# from apps.procurement.models import (
#     Tender, TenderApplication, Vendor, TenderAward,
#     PurchaseOrder, PurchaseItem
# )

# User = get_user_model()
# fake = Faker()

# class Command(BaseCommand):
#     help = 'Seed tenders, applications, vendors, tender awards, and purchase orders'

#     def handle(self, *args, **options):
#         # Create or get admin user
#         user, _ = User.objects.get_or_create(
#             username='admin',
#             defaults={
#                 'email': 'admin@example.com',
#                 'is_staff': True,
#                 'is_superuser': True
#             }
#         )

#         self.stdout.write(self.style.SUCCESS(f"Using user: {user.username}"))

#         # Clear old data
#         PurchaseItem.objects.all().delete()
#         PurchaseOrder.objects.all().delete()
#         TenderAward.objects.all().delete()
#         TenderApplication.objects.all().delete()
#         Vendor.objects.all().delete()
#         Tender.objects.all().delete()

#         tender_titles = [
#             "Supply of Office Furniture",
#             "Provision of Internet Services",
#             "Printing of Exam Booklets",
#             "Procurement of Lab Equipment"
#         ]

#         units = ["pcs", "books", "reams", "sets", "litres"]

#         for title in tender_titles:
#             projected_amount = random.randint(10000, 100000)

#             tender = Tender.objects.create(
#                 title=title,
#                 description=fake.paragraph(nb_sentences=3),
#                 deadline=timezone.now().date() + timedelta(days=random.randint(7, 30)),
#                 created_by=user,
#                 projected_amount=projected_amount
#             )
#             self.stdout.write(self.style.SUCCESS(f"Created Tender: {title}"))

#             for _ in range(random.randint(3, 5)):
#                 company_name = fake.company()
#                 email = fake.company_email()
#                 phone = fake.phone_number()
#                 address = fake.address()

#                 status = random.choices(
#                     ["approved", "pending", "rejected"],
#                     weights=[0.4, 0.4, 0.2],
#                     k=1
#                 )[0]

#                 app = TenderApplication.objects.create(
#                     tender=tender,
#                     company_name=company_name,
#                     email=email,
#                     phone=phone,
#                     address=address,
#                     status=status,
#                     reviewed_by=user if status != "pending" else None,
#                     reviewed_on=timezone.now() if status != "pending" else None
#                 )

#                 self.stdout.write(self.style.SUCCESS(
#                     f"Application: {company_name} — Status: {status}"
#                 ))

#                 if status == "approved" and not TenderAward.objects.filter(tender=tender).exists():
#                     vendor = app.convert_to_vendor()

#                     award_amount = random.randint(int(projected_amount * 0.9), int(projected_amount * 1.1))

#                     if not TenderAward.objects.filter(tender=tender).exists():
#                         TenderAward.objects.create(
#                             tender=tender,
#                             vendor=vendor,
#                             award_amount=award_amount  # Add the award amount
#                         )

#                     self.stdout.write(self.style.SUCCESS(
#                         f"Tender '{tender.title}' awarded to: {vendor.name} for {award_amount}"
#                     ))

#                     # Create a Purchase Order linked to the awarded vendor
#                     po = PurchaseOrder.objects.create(
#                         vendor=vendor,
#                         created_by=user,
#                         status="approved"
#                     )

#                     # Add items to Purchase Order
#                     for i in range(random.randint(1, 4)):
#                         item_name = fake.word().capitalize() + " " + fake.word().capitalize()
#                         unit = random.choice(units)
#                         quantity = random.randint(10, 100)
#                         unit_price = random.randint(500, 5000)

#                         PurchaseItem.objects.create(
#                             purchase_order=po,
#                             name=item_name,
#                             description=fake.sentence(),
#                             quantity=quantity,
#                             unit=unit,
#                             unit_price=unit_price
#                         )

#                     self.stdout.write(self.style.SUCCESS(
#                         f"Purchase Order created for {vendor.name} with {po.items.count()} items"
#                     ))

#         self.stdout.write(self.style.SUCCESS("\n✔ Seeding completed successfully."))
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from faker import Faker
import random
from datetime import timedelta

from apps.procurement.models import (
    Tender, TenderApplication, Vendor, TenderAward,
    PurchaseOrder, PurchaseItem
)
from apps.inventory.models import Category

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Seed tenders, applications, vendors, tender awards, and purchase orders'

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )

        self.stdout.write(self.style.SUCCESS(f"Using user: {user.username}"))

        # Clear old data
        PurchaseItem.objects.all().delete()
        PurchaseOrder.objects.all().delete()
        TenderAward.objects.all().delete()
        TenderApplication.objects.all().delete()
        Vendor.objects.all().delete()
        Tender.objects.all().delete()

        tender_titles = [
            "Supply of Office Furniture",
            "Provision of Internet Services",
            "Printing of Exam Booklets",
            "Procurement of Lab Equipment"
        ]

        units = ["pcs", "books", "reams", "sets", "litres"]
        category_map = {
            "Furniture": "Furniture",
            "Booklets": "Books",
            "Equipment": "Stationery"
        }

        # Create default categories if not exist
        for cat_name in category_map.values():
            Category.objects.get_or_create(name=cat_name)

        for title in tender_titles:
            projected_amount = random.randint(10000, 100000)

            tender = Tender.objects.create(
                title=title,
                description=fake.paragraph(nb_sentences=3),
                deadline=timezone.now().date() + timedelta(days=random.randint(7, 30)),
                created_by=user,
                projected_amount=projected_amount
            )
            self.stdout.write(self.style.SUCCESS(f"Created Tender: {title}"))

            for _ in range(random.randint(3, 5)):
                company_name = fake.company()
                email = fake.company_email()
                phone = fake.phone_number()
                address = fake.address()

                status = random.choices(
                    ["approved", "pending", "rejected"],
                    weights=[0.4, 0.4, 0.2],
                    k=1
                )[0]

                app = TenderApplication.objects.create(
                    tender=tender,
                    company_name=company_name,
                    email=email,
                    phone=phone,
                    address=address,
                    status=status,
                    reviewed_by=user if status != "pending" else None,
                    reviewed_on=timezone.now() if status != "pending" else None
                )

                self.stdout.write(self.style.SUCCESS(f"Application: {company_name} — Status: {status}"))

                if status == "approved" and not TenderAward.objects.filter(tender=tender).exists():
                    vendor = app.convert_to_vendor()
                    award_amount = random.randint(int(projected_amount * 0.9), int(projected_amount * 1.1))

                    if not TenderAward.objects.filter(tender=tender).exists():
                        TenderAward.objects.create(
                            tender=tender,
                            vendor=vendor,
                            award_amount=award_amount
                        )

                    self.stdout.write(self.style.SUCCESS(
                        f"Tender '{tender.title}' awarded to: {vendor.name} for {award_amount}"
                    ))

                    po = PurchaseOrder.objects.create(
                        vendor=vendor,
                        created_by=user,
                        status="approved"
                    )

                    for _ in range(random.randint(1, 4)):
                        item_name = fake.word().capitalize() + " " + fake.word().capitalize()
                        description = fake.sentence()
                        quantity = random.randint(10, 100)
                        unit_price = random.randint(500, 5000)
                        unit = random.choice(units)

                        # Choose category based on tender title keywords
                        matched_cat = next((v for k, v in category_map.items() if k.lower() in title.lower()), None)
                        category = Category.objects.filter(name=matched_cat).first() if matched_cat else None

                        PurchaseItem.objects.create(
                            purchase_order=po,
                            name=item_name,
                            description=description,
                            quantity=quantity,
                            unit=unit,
                            unit_price=unit_price,
                            category=category
                        )

                    self.stdout.write(self.style.SUCCESS(
                        f"Purchase Order created for {vendor.name} with {po.items.count()} items"
                    ))

        self.stdout.write(self.style.SUCCESS("\n✔ Tender and purchase seeding complete."))
