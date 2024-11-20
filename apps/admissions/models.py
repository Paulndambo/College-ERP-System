from django.db import models

from apps.core.models import AbsoluteBaseModel
# Create your models here.
APPLICATION_STATUSES = (
    ("Under Review", "Under Review"),
    ("Declined", "Declined"),
    ("Info Requested", "Info Requested"),
    ("Accepted", "Accepted"),
)
EDUCATION_LEVEL_CHOICES = (
    ("Primary School", "Primary School"),
    ("Secondary School", "Secondary School"),
    ("College", "College"),
    ("University", "University"),
)

class StudentApplication(AbsoluteBaseModel):
    application_number = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    id_number = models.CharField(max_length=255, null=True)
    passport_number = models.CharField(max_length=255, null=True)
    date_of_birth = models.DateField(null=True)
    gender = models.CharField(max_length=255, choices=[('Male', 'Male'), ('Female', 'Female')])
    
    first_choice_programme = models.ForeignKey('schools.Programme', on_delete=models.SET_NULL, null=True, related_name='first_choice_programme')
    second_choice_programme = models.ForeignKey('schools.Programme', on_delete=models.SET_NULL, null=True, related_name='second_choice_programme')
    third_choice_programme = models.ForeignKey('schools.Programme', on_delete=models.SET_NULL, null=True, related_name='third_choice_programme')
    
    guardian_name = models.CharField(max_length=255, null=True)
    guardian_email = models.EmailField(null=True)
    guardian_relationship = models.CharField(max_length=255, null=True)
    guardian_phone_number = models.CharField(max_length=255, null=True)
    
    address = models.CharField(max_length=255, null=True)
    postal_code = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    
    intake_interested = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=255, choices=APPLICATION_STATUSES, default="Under Review")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"      
    
class ApplicationDocument(AbsoluteBaseModel):
    student_application = models.ForeignKey('admissions.StudentApplication', on_delete=models.CASCADE)
    document_name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=255)
    document_file = models.FileField(upload_to='application_documents/')
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.document_name


class ApplicationEducationHistory(AbsoluteBaseModel):
    student_application = models.ForeignKey('admissions.StudentApplication', on_delete=models.CASCADE)
    institution = models.CharField(max_length=255)
    level = models.CharField(max_length=255, choices=EDUCATION_LEVEL_CHOICES)
    grade = models.CharField(max_length=255, null=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True)
    graduated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.user.first_name} {self.student.user.last_name}"