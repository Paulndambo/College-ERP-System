from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from faker import Faker
import random
from datetime import timedelta

from apps.procurement.models import Tender, TenderApplication, Vendor, TenderAward

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Seed tenders, applications, vendors, and tender awards'

    def handle(self, *args, **options):
        # Create or get admin user
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
        Vendor.objects.all().delete()
        TenderAward.objects.all().delete()
        TenderApplication.objects.all().delete()
        Tender.objects.all().delete()

        tender_titles = [
            "Supply of Office Furniture",
            "Provision of Internet Services",
            "Printing of Exam Booklets",
            "Procurement of Lab Equipment"
        ]

        for title in tender_titles:
            tender = Tender.objects.create(
                title=title,
                description=fake.paragraph(nb_sentences=3),
                deadline=timezone.now().date() + timedelta(days=random.randint(7, 30)),
                created_by=user
            )
            self.stdout.write(self.style.SUCCESS(f"Created Tender: {title}"))

            for _ in range(random.randint(3, 5)):
                company_name = fake.company()
                email = fake.company_email()
                phone = fake.phone_number()
                address = fake.address()

                # Determine status
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

                self.stdout.write(self.style.SUCCESS(
                    f"Application: {company_name} — Status: {status}"
                ))

                # If approved and tender not already awarded, convert to vendor and award
                if status == "approved" and not TenderAward.objects.filter(tender=tender).exists():
                    vendor = app.convert_to_vendor()

                    # Create award only for the first approved application
                    if not TenderAward.objects.filter(tender=tender).exists():
                        TenderAward.objects.create(
                            tender=tender,
                            vendor=vendor
                        )

                        self.stdout.write(self.style.SUCCESS(
                            f"Tender '{tender.title}' awarded to: {vendor.name}"
                        ))

        self.stdout.write(self.style.SUCCESS("\n✔ Seeding completed successfully."))
        self.stdout.write(self.style.SUCCESS("Tenders, applications, vendors, and awards have been created."))
