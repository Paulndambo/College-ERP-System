# import csv

# from django.db import transaction

# from apps.library.models import Book


# class BooksUploadMixin(object):
#     def __init__(self, file_path):
#         self.file_path = file_path

#     def run(self):
#         self.__upload_books()

#     @transaction.atomic
#     def __upload_books(self):
#         data = list(csv.DictReader(open(self.file_path)))

#         books_list = [Book(**book) for book in data]
#         Book.objects.bulk_create(books_list)
#         print("********************Books Uploaded Successfully***********************")

import csv
import io
from datetime import datetime
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.library.models import Book


class BooksUploadMixin:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.errors = []
        self.success_count = 0
        self.skipped_count = 0

    def run(self):
        return self._upload_books()

    def _normalize_category(self, category):
        """Normalize category values from CSV to match model choices"""
        category_mapping = {
            "Digital Content": "Digital",
            "digital content": "Digital",
            "Book": "Book",
            "book": "Book",
            "Journal": "Journal",
            "journal": "Journal",
        }
        return category_mapping.get(category, category)

    def _parse_date(self, date_string):
        """Parse date string to date object"""
        if not date_string:
            return None
        try:
            return datetime.strptime(date_string, "%Y-%m-%d").date()
        except ValueError:
            try:
                return datetime.strptime(date_string, "%m/%d/%Y").date()
            except ValueError:
                return None

    def _validate_and_prepare_book_data(self, row):
        """Validate and prepare book data from CSV row"""
        try:
            # Normalize category
            category = self._normalize_category(row.get("category", ""))

            # Parse date
            publication_date = self._parse_date(row.get("publication_date"))

            # Prepare book data
            book_data = {
                "title": row.get("title", "").strip(),
                "author": row.get("author", "").strip(),
                "category": category,
                "isbn": row.get("isbn", "").strip() or None,
                "publication_date": publication_date,
                "copies_available": int(row.get("copies_available", 1)),
                "total_copies": int(row.get("total_copies", 1)),
                "unit_price": float(row.get("unit_price", 0)),
            }

            # Basic validation
            if not book_data["title"]:
                raise ValueError("Title is required")
            if not book_data["author"]:
                raise ValueError("Author is required")
            if category not in ["Book", "Journal", "Digital"]:
                raise ValueError(f"Invalid category: {category}")

            return book_data

        except (ValueError, TypeError) as e:
            raise ValidationError(f"Row validation error: {str(e)}")

    @transaction.atomic
    def _upload_books(self):
        try:
            # Read CSV file
            if hasattr(self.csv_file, "read"):
                content = self.csv_file.read()
                if isinstance(content, bytes):
                    content = content.decode("utf-8")
            else:
                content = self.csv_file

            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(content))
            books_to_create = []

            for row_num, row in enumerate(
                csv_reader, start=2
            ):  # Start from 2 (header is row 1)
                try:
                    book_data = self._validate_and_prepare_book_data(row)

                    # Check if book with same ISBN already exists
                    if (
                        book_data["isbn"]
                        and Book.objects.filter(isbn=book_data["isbn"]).exists()
                    ):
                        self.errors.append(
                            f"Row {row_num}: Book with ISBN {book_data['isbn']} already exists"
                        )
                        self.skipped_count += 1
                        continue

                    books_to_create.append(Book(**book_data))

                except ValidationError as e:
                    self.errors.append(f"Row {row_num}: {str(e)}")
                    continue
                except Exception as e:
                    self.errors.append(f"Row {row_num}: Unexpected error - {str(e)}")
                    continue

            # Bulk create books
            if books_to_create:
                Book.objects.bulk_create(books_to_create, ignore_conflicts=True)
                self.success_count = len(books_to_create)

            return {
                "success": True,
                "message": f"Successfully uploaded {self.success_count} books",
                "success_count": self.success_count,
                "skipped_count": self.skipped_count,
                "errors": self.errors,
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Upload failed: {str(e)}",
                "success_count": 0,
                "skipped_count": 0,
                "errors": [str(e)],
            }
