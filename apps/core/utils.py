from django.db.models import Count, Q
from apps.students.models import Student
from apps.staff.models import Staff
from apps.schools.models import Programme, Department
import uuid
from datetime import datetime
from django.db import transaction


class ModelCountUtils:
    @staticmethod
    def get_active_students_count():
        return Student.objects.filter(status="Active").count()

    @staticmethod
    def get_active_staff_count():
        return Staff.objects.filter(status="Active").count()

    @staticmethod
    def get_programmes_count():
        return Programme.objects.count()

    @staticmethod
    def get_departments_count():
        return Department.objects.count()

    @staticmethod
    def get_academic_departments_count():
        return Department.objects.filter(department_type=Department.ACADEMIC).count()

    @staticmethod
    def get_non_academic_departments_count():
        return Department.objects.filter(
            department_type=Department.NOT_ACADEMIC
        ).count()

    @staticmethod
    def get_all_counts():
        return {
            "active_students": ModelCountUtils.get_active_students_count(),
            "active_staff": ModelCountUtils.get_active_staff_count(),
            "total_programmes": ModelCountUtils.get_programmes_count(),
            "total_departments": ModelCountUtils.get_departments_count(),
        }


def payment_ref_generator(prefix="LIB"):
    """
    Generates a unique payment reference.
    Format: PREFIX-YYYYMMDDHHMMSS-UUID4-short
    Example: LIB-20250626134322-7f3e9a
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{timestamp}-{random_suffix}"


def generate_staff_number(
    department, staff_model, user_model, prefix_length=3, max_attempts=1000
):
    """
    Generate a unique staff number: [DEPTPREFIX][zero-padded sequential number].

    Parameters:
        department: Department instance (must have a `name` attribute)
        staff_model: The model class that has `staff_number` field
        user_model: The user model class to also check for username clashes
        prefix_length: How many characters to take from department name (default=3)
        max_attempts: Maximum number of attempts before raising error

    Returns:
        str: A unique staff number like 'HUM001', 'FIN012', etc.
    """
    dept_prefix = department.name[:prefix_length].upper()

    with transaction.atomic():
        # find the highest existing number for this prefix
        existing_staff = (
            staff_model.objects.filter(staff_number__startswith=dept_prefix)
            .order_by("-staff_number")
            .first()
        )

        if existing_staff:
            try:
                last_number = int(existing_staff.staff_number[len(dept_prefix) :])
            except (ValueError, IndexError):
                last_number = 0
        else:
            last_number = 0

        # Loop until we find a free number
        for i in range(1, max_attempts + 1):
            next_number = last_number + i
            proposed = f"{dept_prefix}{next_number:03d}"

            if (
                not staff_model.objects.filter(staff_number=proposed).exists()
                and not user_model.objects.filter(username=proposed).exists()
            ):
                return proposed

    raise ValueError(f"Unable to generate unique staff number for {department.name}")
