import csv
from decimal import Decimal

from django.db import transaction
from apps.exams.models import ExamData
from apps.students.models import Student


class StudentsMarksUploadMixin(object):
    def __init__(self, file_path, semester_id, course_id, user_id):
        self.file_path = file_path
        self.semester_id = semester_id
        self.course_id = course_id
        self.user_id = user_id

    def run(self):
        self.__upload_marks()

    @transaction.atomic
    def __upload_marks(self):
        marks_data = list(csv.DictReader(open(self.file_path)))

        marks_list = []
        for row in marks_data:
            student = Student.objects.get(
                registration_number=row["registration_number"]
            )
            cat_one = Decimal(row["cat_one"])
            cat_two = Decimal(row["cat_two"])
            exam_marks = Decimal(row["exam_marks"])
            total_marks = ((cat_one + cat_two) / 2) + exam_marks

            marks_list.append(
                ExamData(
                    student=student,
                    semester_id=self.semester_id,
                    course_id=self.course_id,
                    cat_one=cat_one,
                    cat_two=cat_two,
                    exam_marks=exam_marks,
                    recorded_by_id=self.user_id,
                    total_marks=total_marks,
                )
            )

        ExamData.objects.bulk_create(marks_list)

        print("Students Marks Successfully Uploaded!!!")
