import os
import time

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

from django.shortcuts import render, redirect, HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages


fs = FileSystemStorage(location="temp")

from apps.schools.uploads.upload_cohorts_mixin import CohortsUploadMixin


def upload_cohorts(request):
    if request.method == "POST":
        try:
            source_file = request.FILES["cohorts_file"]
            source_file_extension = (
                request.FILES["cohorts_file"].name.split(".")[-1].lower()
            )

            if source_file_extension in ["csv", "CSV"]:
                source_file_content = source_file.read()
                source_file_content = ContentFile(source_file_content)
                source_file_name = fs.save("temp_source_file.csv", source_file_content)
                temp_source_file = fs.path(source_file_name)

                start_time = time.time()
                print(f"Execution Started At: {start_time}")

                csv_uploader = CohortsUploadMixin(temp_source_file)
                csv_uploader.run()

                end_time = time.time()
                elapsed_time = end_time - start_time

                print(f"Execution Ended At: {end_time}")
                print(f"Execution Time: {elapsed_time}")

                return redirect("cohorts")
            else:
                return HttpResponse({"Please upload only .csv files!"})

        except Exception as e:
            raise e
    return render(request, "cohorts/upload_cohorts.html")
