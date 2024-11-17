from apps.core.models import AbsoluteBaseModel


class SchoolFee(AbsoluteBaseModel):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    semester = models.ForeignKey(
        "schools.Semester", on_delete=models.SET_NULL, null=True
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_expected = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.student.user.name} - {self.semester.name}"


class SchoolFeePayment(AbsoluteBaseModel):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=255)
    payment_reference = models.CharField(max_length=255, null=True, blank=True)
