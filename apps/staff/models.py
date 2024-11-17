from django.db import models

from apps.core.models import AbsoluteBaseModel


# Create your models here.
class Department(AbsoluteBaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Staff(AbsoluteBaseModel):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)
    staff_number = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
