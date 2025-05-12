from django.db import models

from apps.core.models import AbsoluteBaseModel

# Create your models here.
PAYMENT_TYPES = (
    ("Fees Payment", "Fees Payment"),
    ("Meal Card Payment", "Meal Card Payment"),
    ("Library Fine Payment", "Library Fine Payment"),
    ("Hostel Payment", "Hostel Payment"),
)

PAYMENT_DIRECTIONS = (
    ("Income", "Income"),
    ("Expense", "Expense"),
)

PAYMENT_METHODS = (
    ("Cash", "Cash"),
    ("Bank Transfer", "Bank Transfer"),
    ("Mobile Money", "Mobile Money"),
    ("Cheque", "Cheque"),
)

BUDGET_STATUSES = (
    ("Under Review", "Under Review"),
    ("Approved", "Approved"),
    ("Declined", "Declined"),
)

class Budget(AbsoluteBaseModel):
    title = models.CharField(max_length=255)
    school = models.ForeignKey("schools.School", on_delete=models.CASCADE, null=True)
    department = models.ForeignKey("schools.Department", on_delete=models.SET_NULL, null=True)
    amount_requested = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    amount_approved = models.DecimalField(max_digits=100, decimal_places=2, default=0)
    status = models.CharField(max_length=255, choices=BUDGET_STATUSES, default="Under Review")
    submitted_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, related_name="budgetsubmitters")
    approved_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, related_name="budgetapprovers")
    description = models.TextField(null=True)

    def __str__(self):
        return self.title
    

class BudgetItem(AbsoluteBaseModel):
    title = models.CharField(max_length=255)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    description = models.TextField(null=True)
    amount = models.DecimalField(max_digits=100, decimal_places=2)

    def __str__(self):
        return self.title
    

class BudgetDocument(AbsoluteBaseModel):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    document_name = models.CharField(max_length=255)
    document_file = models.FileField(upload_to="budget_documents/")

    def __str__(self):
        return self.document_name


class Payment(AbsoluteBaseModel):
    payer = models.ForeignKey("users.User", on_delete=models.SET_NULL, related_name="payers", null=True)
    receiver = models.ForeignKey("users.User", on_delete=models.SET_NULL, related_name="receivers", null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_type = models.CharField(max_length=255, choices=PAYMENT_TYPES)
    direction = models.CharField(max_length=255, choices=PAYMENT_DIRECTIONS)
    recorded_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    payment_method = models.CharField(max_length=255, choices=PAYMENT_METHODS)
    description = models.CharField(max_length=500, null=True)
    payment_reference = models.CharField(max_length=255, null=True)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return self.payment_type


class FeePayment(AbsoluteBaseModel):
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=255, choices=PAYMENT_METHODS)
    payment_reference = models.CharField(max_length=255, null=True, blank=True)
    recorded_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return self.student.user.name + " " + self.payment_type


class LibraryFinePayment(AbsoluteBaseModel):
    member = models.ForeignKey("library.Member", on_delete=models.CASCADE)
    fine = models.OneToOneField("library.Fine", on_delete=models.CASCADE, null=True, related_name="finepayment")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_date = models.DateField(null=True)
    payment_method = models.CharField(max_length=255, choices=PAYMENT_METHODS, null=True)
    payment_reference = models.CharField(max_length=255, null=True, blank=True)
    recorded_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_on"]

    def payment_status(self):
        return "Paid" if self.paid else "Unpaid"


class FeeStructure(AbsoluteBaseModel):
    programme = models.ForeignKey("schools.Programme", on_delete=models.CASCADE)
    year_of_study = models.ForeignKey("core.StudyYear", on_delete=models.SET_NULL, null=True)
    semester = models.ForeignKey("schools.Semester", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{str(self.programme)} - {self.year_of_study.name}, {self.semester.name}"

    def total_amount(self):
        return sum(list(self.feeitems.all().values_list("amount", flat=True)))


class FeeStructureItem(AbsoluteBaseModel):
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name="feeitems")
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.description
