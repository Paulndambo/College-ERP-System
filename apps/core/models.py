from django.db import models


# Create your models here.
class AbsoluteBaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserRole(AbsoluteBaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Campus(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(max_length=255, null=True)
    email = models.EmailField(null=True)
    population = models.IntegerField(null=True)

    def __str__(self):
        return self.name
