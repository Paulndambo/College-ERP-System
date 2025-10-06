
import logging

from apps.students.models import Promotion, SemesterReporting, Student
from apps.core.models import StudyYear

logging.basicConfig(level=logging.DEBUG)

class SemesterReportingMixin:
    """Handles semester reporting and promotions"""

    def report_semester_students(self, cohort, semester, done_by=None):
        students = Student.objects.filter(cohort=cohort, status="Active")
        created = []
        duplicates = []

        for student in students:
            existing = SemesterReporting.objects.filter(student=student, semester=semester).first()
            if existing:
                duplicates.append(existing.id)
            else:
                report = SemesterReporting.objects.create(student=student, semester=semester, done_by=done_by)
                created.append(report.id)

        return {"new_reports": created, "duplicates": duplicates}

    def report_semester_student(self, student, semester, done_by=None):
        reporting, created = SemesterReporting.objects.get_or_create(
            student=student, semester=semester, defaults={"done_by": done_by}
        )
        return reporting

    def promote_students(self, cohort, new_study_year, done_by=None):
        students = Student.objects.filter(cohort=cohort, status="Active")
        for student in students:
            Promotion.objects.create(student=student, study_year=new_study_year, done_by=done_by)
            cohort.current_year = new_study_year
            cohort.save(update_fields=["current_year"])
        return students.count()
    
    def promote_student(self, student, new_study_year, done_by=None):
        """
        Promote a single student to a new study year.
        """
        # update the student
        cohort = student.cohort
        if cohort and cohort.current_year != new_study_year:
            cohort.current_year = new_study_year
            cohort.save(update_fields=["current_year"])
            # optional: create promotion record
            Promotion.objects.create(student=student, study_year=new_study_year, done_by=done_by)
            return student
    def graduate_students(self, cohort, done_by=None):
        """
        Mark all students in a given cohort as Graduated.
        """
        students = Student.objects.filter(cohort=cohort, status="Active")
        count = students.update(status="Graduated")
        # Optionally create a Promotion/Graduation record per student
        # for student in students:
        #     Graduation.objects.create(student=student, done_by=done_by, ...)
        return count
    
    def graduate_student(self, student, done_by=None):
        """
        Mark a single student as graduated.
        """
        student.status = "Graduated"
        student.save(update_fields=["status"])
        # optional Graduation record:
        # Graduation.objects.create(student=student, cohort=student.cohort, done_by=done_by)
        return student
