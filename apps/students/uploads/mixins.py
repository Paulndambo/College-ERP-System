import csv
import time

from django.db import transaction
from apps.students.models import Student
from apps.users.models import User
from apps.core.models import UserRole

from apps.schools.models import ProgrammeCohort, Programme

# Record the start time
start_time = time.time()


class StudentsUploadMixin(object):
    def __init__(self, source_file_path):
        self.source_file_path = source_file_path

    def run(self):
        self.__upload_students()

    @transaction.atomic
    def __upload_students(self):
        csv_data = list(csv.DictReader(open(self.source_file_path)))

        for row in csv_data:
            user = User.objects.create(
                first_name=row["first_name"],
                last_name=row["last_name"],
                email=row["email"],
                gender=row["gender"],
                phone_number=row["phone_number"],
                address=row["address"],
                city=row["city"],
                country=row["country"],
                postal_code=row.get("postal_code"),
                date_of_birth=row["date_of_birth"],
                username=row["registration_number"],
                role=UserRole.objects.get(name="Student"),
            )

            cohort = ProgrammeCohort.objects.filter(name=row["cohort_name"]).first()

            student = Student.objects.create(
                user=user,
                registration_number=row.get("registration_number"),
                guardian_name=row.get("guardian_name"),
                guardian_phone_number=row.get("guardian_phone_number"),
                guardian_relationship=row.get("guardian_relationship"),
                guardian_email=row.get("guardian_email"),
                status=row.get("status") if row.get("status") else "Active",
                cohort=cohort,
                programme=cohort.programme if cohort else None,
            )

        print("Looks like the mixin got a call!!!")
