from django.db import models

from apps.core.models import AbsoluteBaseModel
from apps.exams.grading import generate_grade


# Create your models here.
class ExamData(AbsoluteBaseModel):
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="studentmarks"
    )
    semester = models.ForeignKey(
        "schools.Semester",
        on_delete=models.SET_NULL,
        null=True,
        related_name="semestermarks",
    )
    cohort = models.ForeignKey(
        "schools.ProgrammeCohort",
        on_delete=models.SET_NULL,
        null=True,
        related_name="cohortmarks",
    )
    course = models.ForeignKey("schools.Course", on_delete=models.CASCADE)
    cat_one = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cat_two = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exam_marks = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_marks = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    recorded_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.student.user.name} - {self.semester.name}"

    def cat_marks(self):
        return (self.cat_one + self.cat_two) / 2

    def marks_total(self):
        return (int(self.cat_one + self.cat_two) / 2) + int(self.exam_marks)

    def grade(self):
        return generate_grade(self.marks_total())
