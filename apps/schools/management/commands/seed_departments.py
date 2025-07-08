from django.core.management.base import BaseCommand
from apps.schools.models import Department
from apps.schools.models import School  # Only if needed
from django.db import transaction

class Command(BaseCommand):
    help = "Seed non-academic departments (e.g., Library, Finance, Procurement)"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        non_academic_departments = [
            "Library",
            "Finance",
            "Procurement",
            "Human Resource",
            "Administration",
            "ICT",
            "Maintenance",
            "Security",
            "Health Services",
            "Transport",
        ]
        

        for name in non_academic_departments:
            dept, created = Department.objects.get_or_create(
                name=name,
                defaults={
                    "department_type": Department.NOT_ACADEMIC,
                    "school": None,  # 
                    "office": f"{name} Office"
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {dept.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Already exists: {dept.name}"))

        self.stdout.write(self.style.SUCCESS("Non-academic departments seeded successfully."))
