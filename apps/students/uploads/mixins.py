import csv
import time
from typing import List, Dict, Any

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
        self.success_count = 0
        self.error_count = 0
        self.errors = []

    def run(self):
        self.__upload_students()

    @transaction.atomic
    def __upload_students(self):
        csv_data = list(csv.DictReader(open(self.source_file_path)))
        
        # Pre-fetch required data to avoid N+1 queries
        student_role = UserRole.objects.get(name="Student")
        cohort_cache = {}
        
        # Build cohort cache
        cohort_names = set(row["cohort_name"] for row in csv_data if row.get("cohort_name"))
        cohorts = ProgrammeCohort.objects.filter(name__in=cohort_names).select_related('programme')
        for cohort in cohorts:
            cohort_cache[cohort.name] = cohort

        # Prepare bulk create lists
        users_to_create = []
        students_to_create = []
        
        for row_num, row in enumerate(csv_data, start=2):  # Start from 2 (header is row 1)
            try:
                # Validate required fields
                required_fields = ["first_name", "last_name", "email", "gender", "phone_number", 
                                 "address", "city", "country", "date_of_birth", "registration_number"]
                for field in required_fields:
                    if not row.get(field):
                        self.errors.append(f"Row {row_num}: Missing required field '{field}'")
                        self.error_count += 1
                        continue

                # Check if user already exists
                if User.objects.filter(email=row["email"]).exists():
                    self.errors.append(f"Row {row_num}: User with email {row['email']} already exists")
                    self.error_count += 1
                    continue

                if User.objects.filter(username=row["registration_number"]).exists():
                    self.errors.append(f"Row {row_num}: User with registration number {row['registration_number']} already exists")
                    self.error_count += 1
                    continue

                # Create user object (don't save yet)
                user = User(
                    first_name=row["first_name"].strip(),
                    last_name=row["last_name"].strip(),
                    email=row["email"].strip(),
                    gender=row["gender"].strip(),
                    phone_number=row["phone_number"].strip(),
                    address=row["address"].strip(),
                    city=row["city"].strip(),
                    country=row["country"].strip(),
                    postal_code=row.get("postal_code", "").strip(),
                    date_of_birth=row["date_of_birth"],
                    username=row["registration_number"].strip(),
                    role=student_role,
                )
                users_to_create.append(user)

            except Exception as e:
                self.errors.append(f"Row {row_num}: Error processing user data - {str(e)}")
                self.error_count += 1
                continue

        # Bulk create users
        if users_to_create:
            try:
                created_users = User.objects.bulk_create(users_to_create, ignore_conflicts=True)
                print(f"Successfully created {len(created_users)} users")
                
                # Create a mapping of username to user for student creation
                user_map = {user.username: user for user in created_users}
                
                # Now create students
                for row_num, row in enumerate(csv_data, start=2):
                    try:
                        username = row["registration_number"].strip()
                        user = user_map.get(username)
                        
                        if not user:
                            continue  # User creation failed for this row
                        
                        cohort = cohort_cache.get(row.get("cohort_name"))
                        
                        student = Student(
                            user=user,
                            registration_number=row.get("registration_number", "").strip(),
                            guardian_name=row.get("guardian_name", "").strip(),
                            guardian_phone_number=row.get("guardian_phone_number", "").strip(),
                            guardian_relationship=row.get("guardian_relationship", "").strip(),
                            guardian_email=row.get("guardian_email", "").strip(),
                            status=row.get("status", "Active"),
                            cohort=cohort,
                            programme=cohort.programme if cohort else None,
                        )
                        students_to_create.append(student)
                        
                    except Exception as e:
                        self.errors.append(f"Row {row_num}: Error processing student data - {str(e)}")
                        self.error_count += 1
                        continue

                # Bulk create students
                if students_to_create:
                    created_students = Student.objects.bulk_create(students_to_create, ignore_conflicts=True)
                    self.success_count = len(created_students)
                    print(f"Successfully created {len(created_students)} students")
                
            except Exception as e:
                self.errors.append(f"Bulk creation error: {str(e)}")
                self.error_count += 1

        print(f"Upload completed. Success: {self.success_count}, Errors: {self.error_count}")
        if self.errors:
            print("Errors encountered:")
            for error in self.errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more errors")
