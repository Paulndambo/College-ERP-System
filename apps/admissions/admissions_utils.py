# your_app/utils/application_utils.py

from django.utils import timezone
from .models import StudentApplication


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
