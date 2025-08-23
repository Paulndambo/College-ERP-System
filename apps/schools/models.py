from django.db import models

from apps.core.models import AbsoluteBaseModel
from apps.core.constants import COHORT_YEAR_CHOICES

# Create your models here.
PROGRAMME_TYPES = (
    ("Artisan", "Artisan"),
    ("Certificate", "Certificate"),
    ("Diploma", "Diploma"),
    ("Bachelor", "Bachelor"),
    ("Masters", "Masters"),
    ("PhD", "PhD"),
)



SEMESTER_TYPES = (
    ("Semester One", "Semester One"),
    ("Semester Two", "Semester Two"),
    ("Semester Three", "Semester Three"),
)

COURSE_TYPES = (
    ("Core", "Core"),
    ("Elective", "Elective"),
    ("Optional", "Optional"),
)

class School(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Department(AbsoluteBaseModel):
    ACADEMIC = "Academic"
    NOT_ACADEMIC = "Not Academic"

    DEPARTMENT_TYPE_CHOICES = [
        (ACADEMIC, "Academic"),
        (NOT_ACADEMIC, "Not Academic"),
    ]
    name = models.CharField(max_length=255)
    department_type = models.CharField(
        max_length=15, choices=DEPARTMENT_TYPE_CHOICES, default=ACADEMIC
    )
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    office = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Programme(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, null=True, blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    level = models.CharField(max_length=255, choices=PROGRAMME_TYPES)

    def __str__(self):
        return f"{self.level} of {self.name}"


class Semester(AbsoluteBaseModel):
    name = models.CharField(max_length=255, choices=SEMESTER_TYPES, null=True)
    academic_year = models.CharField(max_length=255)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    status = models.CharField(
        max_length=255, choices=[("Active", "Active"), ("Closed", "Closed")], null=True
    )

    def __str__(self):
        return f"{self.name} - {self.academic_year}"

    def derive_academic_year_from_dates(self):
        """
        Derive academic year - now with a clear hierarchy:
        1. Use cohort intake academic year if available
        2. Fall back to date-based calculation
        """
        if not self.start_date or not self.end_date:
            return ""

        return self._calculate_from_dates()

    def _calculate_from_dates(self):
        start_year = self.start_date.year
        end_year = self.end_date.year
        start_month = self.start_date.month

        if start_year != end_year:
            return f"{start_year}/{end_year}"

        if start_month >= 9:
            return f"{start_year}/{start_year + 1}"
        else:
            return f"{start_year - 1}/{start_year}"

    def save(self, *args, **kwargs):
        """Auto-populate academic_year if not provided"""
        if not self.academic_year and self.start_date and self.end_date:
            self.academic_year = self.derive_academic_year_from_dates()
        super().save(*args, **kwargs)

    def clean(self):
        """Validate that end_date is after start_date"""
        from django.core.exceptions import ValidationError

        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError("End date must be after start date")


class ProgrammeCohort(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    current_year = models.CharField(max_length=255, choices=COHORT_YEAR_CHOICES)
    current_semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    intake = models.ForeignKey("admissions.Intake", on_delete=models.CASCADE, null=True)
    status = models.CharField(
        max_length=255,
        choices=[("Active", "Active"), ("Graduated", "Graduated")],
        default="Active",
    )

    def __str__(self):
        return self.name

    def students_count(self):
        return self.cohortstudents.all().count()

    def get_academic_year(self):
        """Get academic year from the intake this cohort belongs to"""
        return self.intake.get_academic_year()
    

class Course(AbsoluteBaseModel):
    course_code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    study_year = models.CharField(max_length=255, choices=COHORT_YEAR_CHOICES, null=True, blank=True)
    credit_hours = models.FloatField(default=2.0)
    semester = models.CharField(max_length=255, choices=SEMESTER_TYPES, null=True, blank=True)
    course_type = models.CharField(max_length=255, choices=COURSE_TYPES, default="Core")

    def __str__(self):
        return f"{self.name} ({self.course_code})"


class CourseSession(AbsoluteBaseModel):
    cohort = models.ForeignKey(
        ProgrammeCohort, on_delete=models.CASCADE, related_name="cohortsessions"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True)
    period = models.FloatField(default=2)
    status = models.CharField(
        max_length=255,
        choices=[
            ("Future", "Future"),
            ("Active", "Active"),
            ("Completed", "Completed"),
            ("Cancelled", "Cancelled"),
            ("Rescheduled", "Rescheduled"),
        ],
        default="Active",
    )
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name="semesterssessions", null=True, blank=True
    )

    def __str__(self):
        return self.course.name

    def attendance(self):
        return self.sessionattendances.filter(status="Present").count()

    def attendance_percent(self):
        records = self.sessionattendances.all().count()
        attendances = self.attendance()

        value = (attendances / records) * 100

        return f"{round(value, 2)} %"
