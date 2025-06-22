from django.db import models

from apps.core.models import AbsoluteBaseModel
from apps.schools.models import Department
from datetime import timedelta
from django.utils import timezone

# Create your models here.
LEAVE_TYPES = (
    ("Sick Leave", "Sick Leave"),
    ("Vacation Leave", "Vacation Leave"),
    ("Annual Leave", "Annual Leave"),
    ("Maternity Leave", "Maternity Leave"),
    ("Paternity Leave", "Paternity Leave"),
    ("Unpaid Leave", "Unpaid Leave"),
    ("Casual Leave", "Casual Leave"),
    ("Privilege Leave", "Privilege Leave"),
    ("Study Leave", "Study Leave"),
    ("Emergency Leave", "Emergency Leave"),
    ("Other", "Other"),
)

LEAVE_STATUS_CHOICES = (
    ("Active", "Active"),
    ("Completed", "Completed"),
    ("Cancelled", "Cancelled"),
)

STAFF_STATUS_CHOICES = (
    ("Active", "Active"),
    ("Inactive", "Inactive"),
    ("Terminated", "Terminated"),
    ("On Probation", "On Probation"),
)
ONBOARDING_STATUS_CHOICES = (
    ("Not Started", "Not Started"),
    ("In Progress", "In Progress"),
    ("Completed", "Completed"),
)


class StaffPosition(AbsoluteBaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Staff(AbsoluteBaseModel):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)
    staff_number = models.CharField(max_length=255, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    position = models.ForeignKey(
        StaffPosition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20, choices=STAFF_STATUS_CHOICES, default="Inactive"
    )
    onboarding_status = models.CharField(
        max_length=20, choices=ONBOARDING_STATUS_CHOICES, default="Not Started"
    )

    @classmethod
    def generate_staff_number(cls, department):
        """Generate unique staff number with department prefix + sequential number"""
        from apps.users.models import User

        dept_prefix = department.name[:3].upper()
        max_attempts = 1000  # Prevent infinite loops

        for attempt in range(max_attempts):
            # Get the next sequential number
            existing_staff = (
                cls.objects.filter(staff_number__startswith=dept_prefix)
                .order_by("-staff_number")
                .first()
            )

            if existing_staff:
                try:
                    last_number = int(existing_staff.staff_number[3:])
                    next_number = last_number + 1 + attempt
                except ValueError:
                    next_number = 1 + attempt
            else:
                next_number = 1 + attempt

            proposed_staff_number = f"{dept_prefix}{next_number:03d}"

            staff_exists = cls.objects.filter(
                staff_number=proposed_staff_number
            ).exists()
            user_exists = User.objects.filter(username=proposed_staff_number).exists()

            if not staff_exists and not user_exists:
                return proposed_staff_number

        raise ValueError(
            f"Unable to generate unique staff number for department {department.name}"
        )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class StaffLeaveApplication(AbsoluteBaseModel):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=255, choices=LEAVE_TYPES)
    reason = models.CharField(max_length=255)
    
    status = models.CharField(
        max_length=255,
        choices=(
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Declined", "Declined"),
        ),
        default="Pending",
    )
    reason_declined = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.staff.user.first_name} {self.staff.user.last_name}"

    def leave_days_applied_for(self):
        return (self.end_date - self.start_date).days + 1
class StaffLeave(AbsoluteBaseModel):
    application = models.OneToOneField(StaffLeaveApplication, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=255, choices=LEAVE_STATUS_CHOICES, default="Active"
    )
    reason_cancelled = models.CharField(max_length=500, null=True)

    def __str__(self):
        return f"{self.application.staff.user.first_name} {self.application.staff.user.last_name}"

class StaffLeaveEntitlement(models.Model):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE)
    year = models.PositiveIntegerField(default=timezone.now().year)
    total_days = models.PositiveIntegerField(default=21)
    used_days = models.PositiveIntegerField(default=0)

    @property
    def remaining_days(self):
        return self.total_days - self.used_days


class StaffPayroll(AbsoluteBaseModel):
    PAYMENT_FREQUENCY_CHOICES = [
        ("Monthly", "Monthly"),
        ("Bi-Monthly", "Bi-Monthly"),
        ("Weekly", "Weekly"),
        ("Quarterly", "Quarterly"),
    ]
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    house_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0
    )
    other_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    nssf_number = models.CharField(max_length=50, null=True, blank=True)
    nhif_number = models.CharField(max_length=50, null=True, blank=True)
    kra_pin = models.CharField(max_length=50, null=True, blank=True)

    bank_name = models.CharField(max_length=255, null=True, blank=True)
    bank_account_number = models.CharField(max_length=255, null=True, blank=True)
    mpesa_number = models.CharField(
        max_length=12,
        null=True,
        blank=True,
    )
    payment_frequency = models.CharField(
        max_length=20,
        choices=PAYMENT_FREQUENCY_CHOICES,
        default="Monthly",
    )

    def __str__(self):
        return f"Payroll for {self.staff}"


class OvertimeRecords(AbsoluteBaseModel):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    rate_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    approved = models.BooleanField(default=False)


class Payslip(AbsoluteBaseModel):
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("paid", "Paid"),
        ("reversed", "Reversed"),
        ("failed", "Failed"),
    ]
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="payslips")
    payroll_period_start = models.DateField()
    payroll_period_end = models.DateField()

    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    total_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_overtime = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2)
    nssf = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    nhif = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paye = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    generated_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
    )

    def __str__(self):
        return f"Payslip for {self.staff} ({self.payroll_period_start} to {self.payroll_period_end})"


class StaffDocuments(AbsoluteBaseModel):
    staff = models.ForeignKey(
        "Staff", on_delete=models.CASCADE, related_name="documents"
    )
    document_type = models.CharField(
        max_length=100,
        choices=[
            ("ID", "National ID"),
            ("KRA_PIN", "KRA PIN Certificate"),
            ("NHIF", "NHIF Card"),
            ("NSSF", "NSSF Card"),
            ("CV", "Curriculum Vitae"),
            ("Offer Letter", "Offer Letter"),
            ("Career Certifications", "Career Certifications"),
            ("Other", "Other"),
        ],
    )
    document_file = models.FileField(upload_to="staff_documents/")
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.staff} - {self.document_type}"


class StaffOnboardingProgress(AbsoluteBaseModel):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE)
    user_created = models.BooleanField(default=True)
    staff_details_completed = models.BooleanField(default=True)
    payroll_setup_completed = models.BooleanField(default=False)
    documents_uploaded = models.BooleanField(default=False)
    onboarding_completed = models.BooleanField(default=False)
