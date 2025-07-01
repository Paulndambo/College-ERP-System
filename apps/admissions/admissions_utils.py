#

from django.utils import timezone

from apps.students.models import Student
from .models import StudentApplication
from datetime import datetime


def generate_application_number():
    year = timezone.now().year
    prefix = "APP"
    last_application = (
        StudentApplication.objects.filter(
            application_number__startswith=f"{prefix}-{year}-"
        )
        .order_by("-application_number")
        .first()
    )

    if last_application:
        last_number = int(last_application.application_number.split("-")[-1])
        new_number = last_number + 1
    else:
        new_number = 1

    application_number = f"{prefix}-{year}-{new_number:04d}"

    return application_number

def generate_registration_number(programme, level, year):
    name_parts = programme.name.split()
    if len(name_parts) >= 2:
        initials = name_parts[-2][0] + name_parts[-1][0]
    else:
        initials = ''.join([w[0] for w in name_parts[:2]])

    initials = initials.upper()

    
    level_map = {
        "Bachelor": "B",
        "Diploma": "D",
        "Certificate": "C",
        "Artisan": "A",
        "Masters": "M",
        "PhD": "P",
    }

    level_abbr = level_map.get(level, "X")

    
    prefix = f"{initials}/{level_abbr}"
    year = str(year)
    existing_students = Student.objects.filter(
        registration_number__startswith=f"{prefix}-",
        registration_number__endswith=f"/{year}",
    )
    serial_number = f"{existing_students.count() + 1:03}"

    return f"{prefix}-{serial_number}/{year}"

