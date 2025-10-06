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

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class StaffCourseAssignment(AbsoluteBaseModel):
    staff = models.ForeignKey(
        "Staff",
        on_delete=models.CASCADE,
        related_name="course_assignments",  # staff.course_assignments - all assignments
    )
    course = models.ForeignKey(
        "schools.Course",
        on_delete=models.CASCADE,
        related_name="staff_assignments",  # course.staff_assignments - all assignments
    )
    assigned_date = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.staff} - {self.course}"


class LeavePolicy(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    default_days = models.PositiveIntegerField()
    requires_document_after = models.PositiveIntegerField(
        default=0,
        help_text="Require medical certificate or proof if leave exceeds this many consecutive days",
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leave_policies_created",
    )

    def __str__(self):
        return f"{self.name}"


class StaffLeaveApplication(AbsoluteBaseModel):
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name="leave_applications",
        null=True,
        blank=True,
    )
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.ForeignKey(
        LeavePolicy, on_delete=models.CASCADE, related_name="leave_applications"
    )
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


class StaffLeaveEntitlement(AbsoluteBaseModel):
    staff = models.ForeignKey(
        "Staff",
        on_delete=models.CASCADE,
        related_name="leave_balances",
        null=True,
        blank=True,
    )
    leave_type = models.ForeignKey(
        LeavePolicy, on_delete=models.CASCADE, related_name="balances"
    )
    year = models.PositiveIntegerField()
    allocated_days = models.PositiveIntegerField()
    used_days = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    @property
    def remaining_days(self):
        return self.allocated_days - self.used_days

    def __str__(self):
        return f"{self.staff.user.email} - {self.leave_type.name} ({self.year})"


class OvertimeRecords(AbsoluteBaseModel):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    rate_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    approved = models.BooleanField(default=False)


class StaffPaymentMethod(AbsoluteBaseModel):
    """
    Stores staff's payment channels (bank, mobile money, etc.)
    """

    PAYMENT_METHOD_CHOICES = [
        ("bank", "Bank Transfer"),
        ("mpesa", "M-Pesa"),
        ("cash", "Cash"),
        ("other", "Other"),
    ]

    staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="payment_methods"
    )
    method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    bank_name = models.CharField(max_length=255, null=True, blank=True)
    bank_account_number = models.CharField(max_length=255, null=True, blank=True)
    mpesa_number = models.CharField(max_length=20, null=True, blank=True)

    is_primary = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.staff} - {self.get_method_display()}"


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


class Deduction(AbsoluteBaseModel):
    """
    High-level deduction types (NHIF, PAYE, SACCO loan, Union dues, etc.).
    Defines whether this deduction is typically percentage or fixed.
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    DEDUCTION_TYPE_CHOICES = [
        ("percentage", "Percentage Based (with bands)"),
        ("fixed", "Fixed Amount (SACCO, union dues, loans)"),
    ]
    deduction_type = models.CharField(
        max_length=20, choices=DEDUCTION_TYPE_CHOICES, default="percentage"
    )

    is_mandatory = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class DeductionRule(AbsoluteBaseModel):
    """
    Defines the actual rule for a Deduction.

    - For percentage type: fill min_salary, max_salary, and percentage.
    - For fixed type: fill amount only.
    """

    deduction = models.ForeignKey(
        Deduction, on_delete=models.CASCADE, related_name="rules"
    )

    # For percentage-based rules:
    min_salary = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    max_salary = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="For percentage-based deductions.",
    )

    # For fixed deductions (like SACCO, union dues):
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="For fixed deductions.",
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["min_salary"]

    def __str__(self):
        return f"{self.deduction.name} rule"


class StaffDeduction(AbsoluteBaseModel):
    """
    Link a deduction to a specific staff member.
    Useful for SACCO loans, union dues or any deduction that applies to staff.
    All amounts/percentages come from DeductionRule.
    """

    staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="staff_deductions"
    )
    deduction = models.ForeignKey(
        Deduction, on_delete=models.CASCADE, related_name="staff_deductions"
    )

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.staff} - {self.deduction.name}"


class Allowance(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_taxable = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class StaffAllowance(models.Model):
    staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="allowances"
    )
    allowance = models.ForeignKey(Allowance, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    effective_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.staff} - {self.allowance}"


class StaffStatutoryInfo(models.Model):
    """
    Stores all statutory IDs for a staff member
    (KRA, NSSF, NHIF, HELB, etc.)
    """

    staff = models.OneToOneField(
        Staff, on_delete=models.CASCADE, related_name="statutory_info"
    )
    kra_pin = models.CharField(max_length=20, blank=True, null=True)
    nssf_number = models.CharField(max_length=20, blank=True, null=True)
    nhif_number = models.CharField(max_length=20, blank=True, null=True)
    helb_number = models.CharField(max_length=20, blank=True, null=True)  # optional
    other_identifier = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Statutory Info for {self.staff}"


class EmploymentContract(AbsoluteBaseModel):
    PAYMENT_FREQUENCY_CHOICES = [
        ("Monthly", "Monthly"),
        ("Bi-Monthly", "Bi-Monthly"),
        ("Weekly", "Weekly"),
        ("Quarterly", "Quarterly"),
    ]
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    salary_currency = models.CharField(max_length=10, default="KES")
    payment_frequency = models.CharField(
        max_length=20,
        choices=PAYMENT_FREQUENCY_CHOICES,
        default="Monthly",
    )

    def __str__(self):
        return f"Contract for {self.staff}"


class PayrollRun(models.Model):
    period_start = models.DateField()
    period_end = models.DateField()
    STATUS_CHOICES = [
        ("Draft", "Draft"),
        ("Processing", "Processing"),
        ("Completed", "Completed"),
        ("Reversed", "Reversed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Draft")

    def __str__(self):
        return f"Payroll Run {self.period_start} - {self.period_end}"


class Payslip(AbsoluteBaseModel):
    PAYMENT_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Partially Paid", "Partially Paid"),
        ("Processed", "Processed"),
        ("Reversed", "Reversed"),
        ("Failed", "Failed"),
    ]
    payroll_run = models.ForeignKey(
        PayrollRun,
        on_delete=models.CASCADE,
        related_name="payslips",
        blank=True,
        null=True,
    )
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="payslips")
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    total_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_overtime = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2)
    generated_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=50,
        choices=PAYMENT_STATUS_CHOICES,
        default="Pending",
    )

    def __str__(self):
        return f"Payslip for {self.staff} {self.payroll_run}"


class PayslipDeduction(models.Model):
    payslip = models.ForeignKey(
        "Payslip", on_delete=models.CASCADE, related_name="deductions"
    )
    deduction = models.ForeignKey("Deduction", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
