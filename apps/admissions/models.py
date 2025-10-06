from django.db import models
from datetime import datetime
from django.utils.text import slugify
from uuid import uuid4


from apps.core.models import AbsoluteBaseModel

date_today = datetime.now().date()
# Create your models here.
APPLICATION_STATUSES = (
    ("Under Review", "Under Review"),
    ("Declined", "Declined"),
    ("Info Requested", "Info Requested"),
    ("Accepted", "Accepted"),
    ("Draft", "Draft"),
    ("Enrolled", "Enrolled"),
    ("Incomplete", "Incomplete"),
)
EDUCATION_LEVEL_CHOICES = (
    ("Primary School", "Primary School"),
    ("Secondary School", "Secondary School"),
    ("Undergraduate", "Undergraduate"),
    ("Graduate", "Graduate"),
)

DOCUMENT_TYPES = (
    ("Transcript", "Transcript"),
    ("Certificate", "Certificate"),
    ("Identification", "Identification"),
)


class Intake(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    closed = models.BooleanField(default=False)
    academic_year = models.ForeignKey(
        "core.AcademicYear",
        on_delete=models.SET_NULL,
        null=True,
        related_name="intakes",
    )

    def __str__(self):
        return self.name


class StudentApplication(AbsoluteBaseModel):
    application_number = models.CharField(max_length=255, null=True, blank=True)
    lead = models.ForeignKey(
        "marketing.Lead",
        on_delete=models.SET_NULL,
        null=True,
        related_name="leadapplications",
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    id_number = models.CharField(max_length=255, null=True, blank=True)
    passport_number = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField(null=True)
    gender = models.CharField(
        max_length=255, choices=[("Male", "Male"), ("Female", "Female")]
    )

    first_choice_programme = models.ForeignKey(
        "schools.Programme",
        on_delete=models.SET_NULL,
        null=True,
        related_name="first_choice_programme",
    )
    second_choice_programme = models.ForeignKey(
        "schools.Programme",
        on_delete=models.SET_NULL,
        null=True,
        related_name="second_choice_programme",
    )

    guardian_name = models.CharField(max_length=255, null=True, blank=True)
    guardian_email = models.EmailField(null=True, blank=True)
    guardian_relationship = models.CharField(max_length=255, null=True, blank=True)
    guardian_phone_number = models.CharField(max_length=255, null=True, blank=True)

    address = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    passport_photo = models.ImageField(
        upload_to="passport_photos/", null=True, blank=True
    )

    intake = models.ForeignKey(Intake, on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=255, choices=APPLICATION_STATUSES, default="Incomplete"
    )
    slug = models.SlugField(unique=True, null=True)
    campus = models.ForeignKey("core.Campus", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        from apps.admissions.admissions_utils import generate_application_number

        if not self.application_number:
            self.application_number = generate_application_number()
        if not self.slug:
            full_name = f"{self.first_name} {self.last_name}-{uuid4()}"
            self.slug = slugify(full_name)
        super().save(*args, **kwargs)


class ApplicationDocument(AbsoluteBaseModel):
    student_application = models.ForeignKey(
        "admissions.StudentApplication", on_delete=models.CASCADE
    )
    document_name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=255, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to="application_documents/")
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.document_name


class ApplicationEducationHistory(AbsoluteBaseModel):
    student_application = models.ForeignKey(
        "admissions.StudentApplication", on_delete=models.CASCADE
    )
    institution = models.CharField(max_length=255)
    level = models.CharField(max_length=255, choices=EDUCATION_LEVEL_CHOICES)
    grade_or_gpa = models.CharField(max_length=255, null=True)
    year = models.CharField(max_length=255, null=True)
    major = models.CharField(max_length=255, null=True, blank=True)
    graduated = models.BooleanField(default=False)
