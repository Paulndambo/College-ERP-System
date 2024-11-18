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


class School(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Department(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
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


class Course(AbsoluteBaseModel):
    course_code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


SEMESTER_TYPES = (
    ("Semester One", "Semester One"),
    ("Semester Two", "Semester Two"),
    ("Semester Three", "Semester Three"),
)


class Semester(AbsoluteBaseModel):
    name = models.CharField(max_length=255, choices=SEMESTER_TYPES, null=True)
    academic_year = models.CharField(max_length=255)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    status = models.CharField(max_length=255, choices=[("Active", "Active"), ("Closed", "Closed")], null=True)

    def __str__(self):
        return self.name
