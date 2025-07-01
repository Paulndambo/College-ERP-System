import os
import time

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import render, redirect, HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages


fs = FileSystemStorage(location="temp")

from apps.library.uploads.mixins import BooksUploadMixin


# def upload_books(request):
#     if request.method == "POST":
#         try:
#             source_file = request.FILES["books_file"]
#             source_file_extension = (
#                 request.FILES["books_file"].name.split(".")[-1].lower()
#             )

#             if source_file_extension in ["csv", "CSV"]:
#                 source_file_content = source_file.read()
#                 source_file_content = ContentFile(source_file_content)
#                 source_file_name = fs.save("temp_source_file.csv", source_file_content)
#                 temp_source_file = fs.path(source_file_name)

#                 start_time = time.time()
#                 print(f"Execution Started At: {start_time}")

#                 csv_uploader = BooksUploadMixin(temp_source_file)
#                 csv_uploader.run()

#                 end_time = time.time()
#                 elapsed_time = end_time - start_time

#                 print(f"Execution Ended At: {end_time}")
#                 print(f"Execution Time: {elapsed_time}")

#                 return redirect("books")
#             else:
#                 return HttpResponse({"Please upload only .csv files!"})

#         except Exception as e:
#             raise e
#     return render(request, "library/books/upload_books.html")

class BooksUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        try:
            # Get the uploaded file
            books_csv = request.FILES.get('books_csv')
            
            if not books_csv:
                return Response(
                    {'error': 'No file provided. Please upload a CSV file with key "books_csv".'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate file type
            if not books_csv.name.endswith('.csv'):
                return Response(
                    {'error': 'Invalid file type. Please upload a CSV file.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process the upload
            uploader = BooksUploadMixin(books_csv)
            result = uploader.run()
            
            if result['success']:
                response_status = status.HTTP_201_CREATED
                if result['errors']:
                    response_status = status.HTTP_207_MULTI_STATUS
            else:
                response_status = status.HTTP_400_BAD_REQUEST
            
            return Response(result, status=response_status)
            
        except Exception as e:
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
