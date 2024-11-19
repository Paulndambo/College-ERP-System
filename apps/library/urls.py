from django.urls import path

from apps.library.views import (
    BooksListView,
    new_book,
    edit_book,
    delete_book,
    issue_book,
    BookDetailView,
    new_member,
    MembersListView,
    BooksIssuedListView,
    mark_issued_book_as_lost,
    return_issued_book,
    reset_borrowed_book,
    BorrowingFinesListView
)

from apps.library.uploads.views import upload_books
urlpatterns = [
    path("books/", BooksListView.as_view(), name="books"),
    path("books/<int:id>/details/", BookDetailView.as_view(), name="book-details"),
    path("new-book/", new_book, name="new-book"),
    path("edit-book/", edit_book, name="edit-book"),
    path("delete-book/", delete_book, name="delete-book"),
    path("upload-books/", upload_books, name="upload-books"),
    
    path("issue-book/", issue_book, name="issue-book"),
    
    path("members/", MembersListView.as_view(), name="members"),
    path("new-member/", new_member, name="new-member"),
    
    path("issued-books/", BooksIssuedListView.as_view(), name="issued-books"),
    path("return-issued-book/", return_issued_book, name="return-issued-book"),
    path("mark-issued-book-lost/", mark_issued_book_as_lost, name="mark-issued-book-lost"),
    path("reset-issued-book/", reset_borrowed_book, name="reset-issued-book"),
    
    path("borrowing-fines/", BorrowingFinesListView.as_view(), name="borrowing-fines"),
]