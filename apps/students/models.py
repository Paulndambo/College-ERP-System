from datetime import datetime
import calendar

from django.db import models

from apps.core.models import AbsoluteBaseModel

# Create your models here.
STUDENT_STATUS_CHOICES = (
    ("Active", "Active"),
    ("Inactive", "Inactive"),
    ("Graduated", "Graduated"),
    ("Dropped", "Dropped"),
    ("Suspended", "Suspended"),
)
months = [
    ("January", "January"),
    ("February", "February"),
    ("March", "March"),
    ("April", "April"),
    ("May", "May"),
    ("June", "June"),
    ("July", "July"),
    ("August", "August"),
    ("September", "September"),
    ("October", "October"),
    ("November", "November"),
    ("December", "December"),
]


date_today = datetime.now().date()
month_name = calendar.month_name[date_today.month]


class Student(AbsoluteBaseModel):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)
    registration_number = models.CharField(max_length=255)
    guardian_name = models.CharField(max_length=255, null=True)
    guardian_phone_number = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=255, choices=STUDENT_STATUS_CHOICES)
    programme = models.ForeignKey(
        "schools.Programme", on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return (
            f"{self.user.first_name} {self.user.last_name}: {self.registration_number}"
        )


class StudentDocument(AbsoluteBaseModel):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="student_documents/", null=True, blank=True)

    def __str__(self):
        return f"{self.student.user.username}: {self.document.name}"


class MealCard(AbsoluteBaseModel):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    card_number = models.CharField(max_length=255)
    month = models.CharField(max_length=255, choices=months, default=month_name)
    year = models.IntegerField(default=date_today.year)
    expiry_date = models.DateField()

    def __str__(self):
        return f"{self.student.user.username}: {self.card_number}"
