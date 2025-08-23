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
    address = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    population = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class CheckIn(AbsoluteBaseModel):
    user = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True)
    recorded_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="checkinofficers",
    )

    def __str__(self):
        return self.user.first_name


class StudyYear(AbsoluteBaseModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# Permissions
class Module(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class RolePermission(AbsoluteBaseModel):
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    can_view = models.BooleanField(default=True)
    can_create = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_approve = models.BooleanField(default=False)
    can_export = models.BooleanField(default=False)
    can_print = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.role.name} - {self.module.name}"

class AcademicYear(AbsoluteBaseModel):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name
