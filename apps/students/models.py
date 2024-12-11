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

ATTENDANCE_STATUS_CHOICES = (
    ("Present", "Present"),
    ("Absent", "Absent"),
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
    cohort = models.ForeignKey(
        "schools.ProgrammeCohort",
        on_delete=models.SET_NULL,
        null=True,
        related_name="cohortstudents",
    )
    hostel_room = models.ForeignKey(
        "hostels.HostelRoom", on_delete=models.SET_NULL, null=True
    )
    campus = models.ForeignKey("core.Campus", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return (
            f"{self.user.first_name} {self.user.last_name}: {self.registration_number}"
        )


class StudentEducationHistory(AbsoluteBaseModel):
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="educationhistory"
    )
    institution = models.CharField(max_length=255)
    level = models.CharField(max_length=255, choices=EDUCATION_LEVEL_CHOICES)
    grade_or_gpa = models.CharField(max_length=255, null=True)
    major = models.CharField(max_length=255, null=True)
    year = models.CharField(max_length=255, null=True)
    graduated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.user.first_name} {self.student.user.last_name}"


class StudentDocument(AbsoluteBaseModel):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    document_type = models.CharField(max_length=255, null=True)
    document_name = models.CharField(max_length=255)
    document_file = models.FileField(
        upload_to="student_documents/", null=True, blank=True
    )

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


class StudentAttendance(AbsoluteBaseModel):
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="studentattendances"
    )
    session = models.ForeignKey(
        "schools.CourseSession",
        on_delete=models.CASCADE,
        related_name="sessionattendances",
    )
    date = models.DateField()
    status = models.CharField(
        max_length=255, choices=ATTENDANCE_STATUS_CHOICES, default="Present"
    )
    reason = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.student.user.username}: {self.date}"


class StudentCheckIn(AbsoluteBaseModel):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True)
    recorded_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="studentcheckinofficers",
    )

    def __str__(self):
        return self.user.first_name

    def checked_out(self):
        return "Yes" if self.check_out_time else "No"
