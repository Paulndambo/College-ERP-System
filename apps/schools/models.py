from django.db import models

from apps.core.models import AbsoluteBaseModel

# Create your models here.
PROGRAMME_TYPES = (
    ("Artisan", "Artisan"),
    ("Certificate", "Certificate"),
    ("Diploma", "Diploma"),
    ("Bachelor", "Bachelor"),
    ("Masters", "Masters"),
    ("PhD", "PhD"),
)

COHORT_YEAR_CHOICES = (
    ("First Year", "First Year"),
    ("Second Year", "Second Year"),
    ("Third Year", "Third Year"),
    ("Fourth Year", "Fourth Year"),
    ("Fifth Year", "Fifth Year"),
    ("Sixth Year", "Sixth Year"),
    ("Seventh Year", "Seventh Year"),
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
    name = models.CharField(max_length=255, blank=True, null=True)
    academic_year = models.ForeignKey(
        "core.AcademicYear", on_delete=models.CASCADE, related_name="semesters"
    )
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    status = models.CharField(
        max_length=255, choices=[("Active", "Active"), ("Closed", "Closed")], null=True
    )

    def __str__(self):
        return self.name


class ProgrammeCohort(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    current_year = models.ForeignKey(
        "core.StudyYear",
        on_delete=models.CASCADE,
        related_name="cohorts",
        blank=True,
        null=True,
    )
    current_semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="semesters_cohorts",
        blank=True,
        null=True,
    )
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


class Course(AbsoluteBaseModel):
    course_code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    study_year = models.ForeignKey(
        "core.StudyYear", on_delete=models.CASCADE, related_name="courses"
    )
    credit_hours = models.FloatField(default=2.0)
    semester = models.ForeignKey(
        "Semester", on_delete=models.CASCADE, related_name="courses",
        null=True,
        blank=True,
    )
    course_type = models.CharField(max_length=255, 
                                   choices=COURSE_TYPES,
                                   default="Core")

    def __str__(self):
        return self.name


class CourseSession(AbsoluteBaseModel):
    cohort = models.ForeignKey(
        ProgrammeCohort, on_delete=models.CASCADE, related_name="cohortsessions"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="coursesessions"
    )
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
        Semester,
        on_delete=models.CASCADE,
        related_name="semesterssessions",
        null=True,
        blank=True,
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
