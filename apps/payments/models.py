from django.db import models
from datetime import datetime
import calendar

from apps.core.models import AbsoluteBaseModel

# Create your models here.
months = [
    ("January", "January"),
    ("February", "February"),
    ("March", "March"),
    ("April", "April"),
    ("May", "May"),
    ("June", "June"),
    ("July", "July"),
    ("August", "August"),
    ("September", "September"),
    ("October", "October"),
    ("November", "November"),
    ("December", "December"),
]


date_today = datetime.now().date()
month_name = calendar.month_name[date_today.month]


class RentPayment(AbsoluteBaseModel):
    transaction_code = models.CharField(max_length=255, null=True)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.CharField(max_length=255, choices=months, default=month_name)
    year = models.IntegerField(default=date_today.year)
    payment_date = models.DateField()

    def __str__(self):
        return f"{self.student.user.username}: {self.amount}"


class MealCardPayment(AbsoluteBaseModel):
    card_number = models.CharField(max_length=255, null=True)
    mealcard = models.OneToOneField(
        "students.MealCard", on_delete=models.CASCADE, null=True
    )
    transaction_code = models.CharField(max_length=255, null=True)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.CharField(max_length=255, choices=months, default=month_name)
    year = models.IntegerField(default=date_today.year)
    payment_date = models.DateField()

    def __str__(self):
        return f"{self.student.user.username}: {self.amount}"
