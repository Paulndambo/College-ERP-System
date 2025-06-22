

from apps.finance.models import FeeStructure
from apps.students.models import Student, SemesterReporting
from apps.schools.models import ProgrammeCohort, Semester

def promote_students_to_next_semester(cohort: ProgrammeCohort, next_semester: Semester):
    """
    Promote all students in the given cohort to the next semester.
    Also records a SemesterReporting entry.
    """
    already_reported = SemesterReporting.objects.filter(
        cohort=cohort,
        semester=next_semester,
    ).exists()
    if cohort.intake is None:
        raise ValueError("Cohort has no intake assigned. Cannot determine academic year.")

    if already_reported:
        raise ValueError("This cohort has already reported to the next semester.")
    students = Student.objects.filter(cohort=cohort)
    
    skipped_students = []
    for student in students:
        has_fee_structure = FeeStructure.objects.filter(
            programme=student.programme,
            semester__name=next_semester.name
        ).exists()

        if not has_fee_structure:
            skipped_students.append(student)
            continue

        SemesterReporting.objects.get_or_create(
            student=student,
            semester=next_semester,
            cohort=cohort,
            academic_year=cohort.get_academic_year(),
            reported=True
        )

    cohort.current_semester = next_semester
    cohort.save()
    return skipped_students
