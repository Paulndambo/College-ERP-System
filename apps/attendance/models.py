from django.db import models

from apps.core.models import AbsoluteBaseModel
# Create your models here.
class StaffCheckIn(AbsoluteBaseModel):
    staff = models.ForeignKey(
        "staff.Staff",
        on_delete=models.CASCADE,
        related_name="check_in",
        verbose_name="Staff",
    )
    check_in_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Check In Time",
    )
    check_out_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Check Out Time",
    )

    class Meta:
        verbose_name = "Staff Check In"
        verbose_name_plural = "Staff Check Ins"

    def __str__(self):
        return f"{self.staff} - {self.check_in_time}"
