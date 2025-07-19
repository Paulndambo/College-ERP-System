from django.db.models import Count, Q
from apps.students.models import Student
from apps.staff.models import Staff
from apps.schools.models import Programme, Department
import uuid
from datetime import datetime


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
