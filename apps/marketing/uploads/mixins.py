import csv
from apps.marketing.models import Lead


class UploadLeadsMixin(object):
    def __init__(self, file_path):
        self.file_path = file_path

    def run(self):
        self.__upload_leads()

    def __upload_leads(self):
        data = list(csv.DictReader(open(self.file_path)))

        leads_list = []
        for lead in data:
            leads_list.append(
                Lead(
                    name=lead.get("name"),
                    email=lead.get("email"),
                    gender=lead.get("gender"),
                    phone_number=lead.get("phone_number"),
                    source=lead.get("source"),
                    city=lead.get("city", "N/A"),
                    country=lead.get("country", "N/A"),
                )
            )

        Lead.objects.bulk_create(leads_list)
