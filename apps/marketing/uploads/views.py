from datetime import datetime, timedelta
import calendar

import os
import time

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from django.db import transaction

from apps.marketing.uploads.mixins import UploadLeadsMixin

fs = FileSystemStorage(location="temp")


def upload_leads(request):
    if request.method == "POST":
        try:
            source_file = request.FILES.get("leads_file")
            source_file_extension = (
                request.FILES["leads_file"].name.split(".")[-1].lower()
            )

            if source_file_extension in ["csv", "CSV"]:
                source_file_content = source_file.read()
                source_file_content = ContentFile(source_file_content)
                source_file_name = fs.save("temp_source_file.csv", source_file_content)
                temp_source_file = fs.path(source_file_name)

                start_time = time.time()
                print(f"Execution Started At: {start_time}")

                csv_uploader = UploadLeadsMixin(temp_source_file)
                csv_uploader.run()

                end_time = time.time()
                elapsed_time = end_time - start_time

                print(f"Execution Ended At: {end_time}")
                print(f"Execution Time: {elapsed_time}")

                return redirect("leads")
            else:
                return HttpResponse({"Please upload only .csv files!"})

        except Exception as e:
            raise e

    return render(request, "marketing/leads/upload_leads.html")
