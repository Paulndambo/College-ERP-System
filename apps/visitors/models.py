from django.db import models

from apps.core.models import AbsoluteBaseModel


# Create your models here.
class Visitor(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    id_number = models.CharField(max_length=255, null=True)
    email = models.EmailField(max_length=255, null=True)
    phone = models.CharField(max_length=255, null=True)
    gender = models.CharField(max_length=255, null=True)
    purpose = models.CharField(max_length=255)
    recorded_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    checkin_time = models.DateTimeField(auto_now_add=True)
    checkout_time = models.DateTimeField(null=True)

    def __str__(self):
        return self.name

    def checked_out(self):
        return "Yes" if self.checkout_time else "No"
