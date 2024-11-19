import csv

from django.db import transaction
from apps.schools.models import Programme, Semester, Course, ProgrammeCohort
class CohortsUploadMixin(object):
    def __init__(self, file_path):
        self.file_path = file_path
        
    def run(self):
        self.__upload_cohorts()
        
    @transaction.atomic
    def __upload_cohorts(self):
        data = list(csv.DictReader(open(self.file_path)))
        cohorts_list = []
        for x in data:
            programme = Programme.objects.get(code=x["programme_code"])
            semester = Semester.objects.get(name=x["semester_name"])
            
            cohorts_list.append(
                ProgrammeCohort(
                    name=x["name"],
                    programme=programme,
                    current_semester=semester,
                    current_year=x["current_year"],
                    status=x["status"]
                )
            )
        ProgrammeCohort.objects.bulk_create(cohorts_list)
            