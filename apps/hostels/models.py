from django.db import models

from apps.core.models import AbsoluteBaseModel

# Create your models here.
BOOKING_STATUSES = (
    ("Pending", "Pending"),
    ("Confirmed", "Confirmed"),
    ("Cancelled", "Cancelled"),
)

GENDER_CHOICES = (
    ("Male", "Male"),
    ("Female", "Female"),
    ("Mixed", "Mixed"),
)


class Hostel(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    rooms = models.IntegerField(default=1)
    room_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    capacity = models.IntegerField(default=1)
    gender = models.CharField(max_length=255, choices=GENDER_CHOICES, null=True)
    campus = models.ForeignKey("core.Campus", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class HostelRoom(AbsoluteBaseModel):
    hostel = models.ForeignKey("hostels.Hostel", on_delete=models.CASCADE, null=True)
    room_number = models.CharField(max_length=255)
    room_capacity = models.IntegerField(default=1)
    students_assigned = models.IntegerField(default=0)

    def __str__(self):
        return self.room_number

    def fully_occupied(self):
        return self.students_assigned >= self.room_capacity

    def status(self):
        return "Fully Occupied" if self.fully_occupied() else "Available"

    def get_current_bookings_count(self):
        """Helper method to get actual booking count"""
        return Booking.objects.filter(hostel_room=self).count()

    def occupancy(self):
        if self.room_capacity == 0:
            return "-"
        amount = (self.students_assigned / self.room_capacity) * 100
        return f"{amount:.1f}%"


class Booking(AbsoluteBaseModel):
    student = models.OneToOneField(
        "students.Student", on_delete=models.CASCADE, null=True
    )
    hostel_room = models.ForeignKey(
        "hostels.HostelRoom", on_delete=models.CASCADE, null=True
    )
    status = models.CharField(
        max_length=255, choices=BOOKING_STATUSES, default="Pending"
    )

    def __str__(self):
        if self.student is None:
            return "No student assigned"
        return f"{self.student.user.first_name} {self.student.user.last_name}"
