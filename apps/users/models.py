from django.db import models
from django.contrib.auth.models import AbstractUser

from apps.core.models import AbsoluteBaseModel, UserRole

# Create your models here.
GENDER_CHOICES = (
    ("Male", "Male"),
    ("Female", "Female"),
)


class User(AbstractUser, AbsoluteBaseModel):
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    date_of_birth = models.DateField(null=True)

    def __str__(self):
        return self.username

    def name(self):
        return f"{self.first_name} {self.last_name}"
