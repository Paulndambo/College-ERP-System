from django.db import models

from apps.core.models import AbsoluteBaseModel


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

class Department(AbsoluteBaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class StaffPosition(AbsoluteBaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Staff(AbsoluteBaseModel):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)
    staff_number = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    position = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class StaffLeaveApplication(AbsoluteBaseModel):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=255, choices=LEAVE_TYPES)
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=255, choices=(("Pending", "Pending"), ("Approved", "Approved"), ("Declined", "Declined")), default="Pending")
    reason_declined = models.CharField(max_length=500, null=True)

    def __str__(self):
        return f"{self.staff.user.first_name} {self.staff.user.last_name}"


class StaffLeave(AbsoluteBaseModel):
    application = models.OneToOneField(StaffLeaveApplication, on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=LEAVE_STATUS_CHOICES, default="Active")
    reason_cancelled = models.CharField(max_length=500, null=True)

    def __str__(self):
        return f"{self.application.staff.user.first_name} {self.application.staff.user.last_name}"