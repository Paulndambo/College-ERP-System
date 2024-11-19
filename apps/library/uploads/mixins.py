import csv

from django.db import transaction

from apps.library.models import Book

class BooksUploadMixin(object):
    def __init__(self, file_path):
        self.file_path = file_path
        
    
    def run(self):
        self.__upload_books()
        
        
    @transaction.atomic
    def __upload_books(self):
        data = list(csv.DictReader(open(self.file_path)))
        
        books_list = [Book(**book) for book in data]
        Book.objects.bulk_create(books_list)
        print("********************Books Uploaded Successfully***********************")