from django.db import models
from django.contrib.auth.models import AbstractUser

from apps.core.models import AbsoluteBaseModel, UserRole
import random
from django.utils import timezone
from datetime import timedelta
from django.conf import settings


GENDER_CHOICES = (
    ("Male", "Male"),
    ("Female", "Female"),
)


def generate_otp():
    return f"{random.randint(100000, 999999)}" 

class EmailVerificationOTP(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, default=generate_otp)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10) 

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, default=generate_otp)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"Reset OTP for {self.user.email}"

class User(AbstractUser, AbsoluteBaseModel):
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=255)
    id_number = models.CharField(max_length=255, null=True)
    passport_number = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    postal_code = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    date_of_birth = models.DateField(null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    def name(self):
        return f"{self.first_name} {self.last_name}"
