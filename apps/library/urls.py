from django.urls import path

from apps.library.uploads.views import BooksUploadView

from .views import (
    BookCreateAPIView,
    BookDetailAPIView,
    BookListAPIView,
    BookUpdateAPIView,
    BorrowTransactionCreateView,
    BorrowTransactionListView,
    BorrowTransactionUpdateView,
    FineListView,
    FinePaymentRequestView,
    MemberCreateAPIView,
    MemberDeactivateView,
    MemberDetailAPIView,
    MemberListAPIView,
    MemberReactivateView,
    MemberUpdateAPIView,
)


urlpatterns = [
    path("members/list/", MemberListAPIView.as_view(), name="members"),
    path("members/create/", MemberCreateAPIView.as_view(), name="create-member"),
    path(
        "members/update/<int:pk>/", MemberUpdateAPIView.as_view(), name="update-member"
    ),
    path(
        "members/details/<int:pk>/",
        MemberDetailAPIView.as_view(),
        name="member-details",
    ),
    path(
        "members/deactivate/<int:pk>/",
        MemberDeactivateView.as_view(),
        name="deactivate-member",
    ),
    path(
        "members/activate/<int:pk>/",
        MemberReactivateView.as_view(),
        name="activate-member",
    ),
    path("books/create/", BookCreateAPIView.as_view(), name="books-create"),
    path("books/list/", BookListAPIView.as_view(), name="books-list"),
    path("books/update/<int:pk>/", BookUpdateAPIView.as_view(), name="books-update"),
    path("books/details/<int:pk>/", BookDetailAPIView.as_view(), name="book-details"),
     path('books/upload/', BooksUploadView.as_view(), name='books-upload'),
    path(
        "borrowed-books/create/",
        BorrowTransactionCreateView.as_view(),
        name="issue-book",
    ),
    path(
        "borrowed-books/update/<int:pk>/",
        BorrowTransactionUpdateView.as_view(),
        name="update-issude-book",
    ),
    path(
        "borrowed-books/list/",
        BorrowTransactionListView.as_view(),
        name="borrowed-books-record",
    ),
    path(
        "borrowed-books-fines/list/",
        FineListView.as_view(),
        name="borrowed-books-fines",
    ),
    path(
        "fine-payment-request/",
        FinePaymentRequestView.as_view(),
        name="request-fine-payment",
    ),
]
