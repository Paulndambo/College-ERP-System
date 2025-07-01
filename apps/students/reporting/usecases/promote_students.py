from apps.finance.models import FeeStructure
from apps.students.models import Student, SemesterReporting
from apps.schools.models import ProgrammeCohort, Semester
from django.db import transaction


def promote_students_to_next_semester(cohort: ProgrammeCohort, next_semester: Semester):
    """
    Promote all students in the given cohort to the next semester.
    Only promotes students if a FeeStructure exists for their programme and semester.
    Updates the cohort's current semester only if at least one student is promoted.
    Returns a list of students who were skipped due to missing fee structures.
    """
    print(
        f"--- PROMOTING STUDENTS FOR COHORT: {cohort.name} TO SEMESTER: {next_semester.name} ({next_semester.id}) ---"
    )

    if cohort.intake is None:
        raise ValueError(
            "Cohort has no intake assigned. Cannot determine academic year."
        )

    if SemesterReporting.objects.filter(cohort=cohort, semester=next_semester).exists():
        raise ValueError("This cohort has already reported to the next semester.")

    students = Student.objects.filter(cohort=cohort)
    print(f"Total students in cohort: {students.count()}")

    skipped_students = []
    promoted = False

    with transaction.atomic():
        for student in students:
            print(f"\nProcessing student: {student.id} - {student}")

            has_fee_structure = FeeStructure.objects.filter(
                programme=student.programme, semester=next_semester
            ).exists()

            print(
                f"  - Fee structure exists: {has_fee_structure} for programme: {student.programme} and semester: {next_semester.id}"
            )

            if not has_fee_structure:
                print(
                    f"  → Skipping student {student.id} due to missing fee structure."
                )
                skipped_students.append(student)
                continue

            reporting, created = SemesterReporting.objects.get_or_create(
                student=student,
                semester=next_semester,
                cohort=cohort,
                academic_year=cohort.get_academic_year(),
                defaults={"reported": True},
            )

            if created:
                promoted = True
                print(f"  - Semester reporting created for student {student.id}")
            else:
                print(
                    f"  - Semester reporting already existed for student {student.id}"
                )

        if promoted:
            cohort.current_semester = next_semester
            cohort.save()
            print(
                f"\n✓ Cohort {cohort.name} updated to current semester: {next_semester.name} ({next_semester.id})"
            )
        else:
            print("\n⚠ No students promoted — cohort semester NOT updated.")

    print(f"Skipped students count: {len(skipped_students)}")

    return skipped_students


# def promote_students_to_next_semester(cohort: ProgrammeCohort, next_semester: Semester):
#     """
#     Promote all students in the given cohort to the next semester.
#     Also records a SemesterReporting entry.
#     """
#     print(f"--- PROMOTING STUDENTS FOR COHORT: {cohort.name} TO SEMESTER: {next_semester.name} ({next_semester.id}) ---")

#     already_reported = SemesterReporting.objects.filter(
#         cohort=cohort,
#         semester=next_semester,
#     ).exists()

#     if cohort.intake is None:
#         raise ValueError("Cohort has no intake assigned. Cannot determine academic year.")

#     if already_reported:
#         raise ValueError("This cohort has already reported to the next semester.")

#     students = Student.objects.filter(cohort=cohort)
#     print(f"Total students in cohort: {students.count()}")

#     skipped_students = []

#     for student in students:
#         print(f"\nProcessing student: {student.id} - {student}")

#         has_fee_structure = FeeStructure.objects.filter(
#             programme=student.programme,
#             semester=next_semester
#         ).exists()

#         print(f"  - Fee structure exists: {has_fee_structure} for programme: {student.programme} and semester: {next_semester.id}")

#         if not has_fee_structure:
#             print(f"  → Skipping student {student.id} due to missing fee structure.")
#             skipped_students.append(student)
#             continue

#         reporting, created = SemesterReporting.objects.get_or_create(
#             student=student,
#             semester=next_semester,
#             cohort=cohort,
#             academic_year=cohort.get_academic_year(),
#             reported=True,
#         )

#         print(f"  - Semester reporting {'created' if created else 'already existed'} for student {student.id}")

#     cohort.current_semester = next_semester
#     cohort.save()
#     print(f"\n✓ Cohort {cohort.name} updated to current semester: {next_semester.name} ({next_semester.id})")
#     print(f"Skipped students count: {len(skipped_students)}")

#     return skipped_students
