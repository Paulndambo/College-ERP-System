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

EDUCATION_LEVEL_CHOICES = (
    ("Primary School", "Primary School"),
    ("Secondary School", "Secondary School"),
    ("College", "College"),
    ("University", "University"),
)

date_today = datetime.now().date()
month_name = calendar.month_name[date_today.month]


class Student(AbsoluteBaseModel):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)
    registration_number = models.CharField(max_length=255)
    guardian_name = models.CharField(max_length=255, null=True)
    guardian_phone_number = models.CharField(max_length=255, null=True)
    guardian_relationship = models.CharField(max_length=255, null=True)
    guardian_email = models.EmailField(null=True)
    status = models.CharField(max_length=255, choices=STUDENT_STATUS_CHOICES)
    programme = models.ForeignKey(
        "schools.Programme", on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return (
            f"{self.user.first_name} {self.user.last_name}: {self.registration_number}"
        )
        
class StudentEducationHistory(AbsoluteBaseModel):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="educationhistory")
    institution = models.CharField(max_length=255)
    level = models.CharField(max_length=255, choices=EDUCATION_LEVEL_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True)
    graduated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.user.first_name} {self.student.user.last_name}: {self.name}"


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


class StudentProgramme(AbsoluteBaseModel):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    programme = models.ForeignKey("schools.Programme", on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True)
    current_year = models.CharField(max_length=255, null=True)
    current_semester = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.student.user.username}: {self.programme.name}"