from datetime import datetime
from django.shortcuts import render, redirect
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from django.db import transaction


from django.views.generic import ListView
from django.http import JsonResponse

from apps.library.models import Book, BorrowTransaction, Member, Fine
from apps.users.models import User
from apps.finance.models import LibraryFinePayment

date_today = datetime.now().date()

# Create your views here.
BOOK_CATEGORIES = ["Book", "Journal", "Digital"]


class BooksListView(ListView):
    model = Book
    template_name = "library/books/books.html"
    context_object_name = "books"
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(title__icontains=search_query)
                | Q(author__icontains=search_query)
            )

        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["book_categories"] = BOOK_CATEGORIES
        return context


class BookDetailView(ListView):
    model = BorrowTransaction
    template_name = "library/books/book_details.html"
    context_object_name = "borrowings"
    paginate_by = 6

    book = Book.objects.none()
    members = Member.objects.all()

    def get_queryset(self):
        book_id = self.kwargs["id"]  # Access the 'id' parameter from the URL
        queryset = super().get_queryset().filter(book_id=book_id)
        search_query = self.request.GET.get("search", "")

        self.book = Book.objects.get(id=book_id)

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(member__user__first_name__icontains=search_query)
            )

        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get(
            "search", ""
        )  # Pass the search query back to the template
        context["book"] = self.book
        context["members"] = self.members
        return context


def new_book(request):
    if request.method == "POST":
        title = request.POST.get("title")
        author = request.POST.get("author")
        category = request.POST.get("category")
        isbn = request.POST.get("isbn")
        publication_date = request.POST.get("publication_date")
        copies_available = request.POST.get("copies_available")
        total_copies = request.POST.get("total_copies")
        unit_price = request.POST.get("unit_price")

        Book.objects.create(
            title=title,
            author=author,
            category=category,
            isbn=isbn,
            publication_date=publication_date,
            copies_available=copies_available,
            total_copies=total_copies,
            unit_price=unit_price,
        )

        return redirect("books")
    return render(request, "library/books/new_book.html")


def edit_book(request):
    if request.method == "POST":
        book_id = request.POST.get("book_id")
        title = request.POST.get("title")
        author = request.POST.get("author")
        category = request.POST.get("category")
        isbn = request.POST.get("isbn")
        publication_date = request.POST.get("publication_date")
        copies_available = request.POST.get("copies_available")
        total_copies = request.POST.get("total_copies")
        unit_price = request.POST.get("unit_price")

        book = Book.objects.get(id=book_id)
        book.title = title
        book.author = author
        book.category = category
        book.isbn = isbn
        book.publication_date = publication_date
        book.copies_available = copies_available
        book.total_copies = total_copies
        book.unit_price = unit_price
        book.save()
        return redirect("books")
    return render(request, "library/books/edit_book.html")


def delete_book(request):
    if request.method == "POST":
        book_id = request.POST.get("book_id")
        book = Book.objects.get(id=book_id)
        book.delete()
        return redirect("books")
    return render(request, "library/books/delete_book.html")


def issue_book(request):
    if request.method == "POST":
        book_id = request.POST.get("book_id")
        member_id = request.POST.get("member_id")
        book_number = request.POST.get("book_number")
        due_date = request.POST.get("due_date")

        issued_book = BorrowTransaction.objects.create(
            book_id=book_id, member_id=member_id
        )
        issued_book.book.copies_available -= 1
        issued_book.book.save()

        issued_book.book_number = book_number if book_number else issued_book.book.isbn
        issued_book.due_date = due_date if due_date else None
        issued_book.save()

        return redirect(f"/library/books/{book_id}/details")
    return render(request, "library/books/issue_book.html")


def issue_member_book(request):
    if request.method == "POST":
        book_id = request.POST.get("book_id")
        member_id = request.POST.get("member_id")
        book_number = request.POST.get("book_number")
        due_date = request.POST.get("due_date")

        issued_book = BorrowTransaction.objects.create(
            book_id=book_id, member_id=member_id
        )
        issued_book.book.copies_available -= 1
        issued_book.book.save()

        issued_book.book_number = book_number if book_number else issued_book.book.isbn
        issued_book.due_date = due_date if due_date else None
        issued_book.save()

        return redirect(f"/library/members/{member_id}/details")
    return render(request, "library/members/issue_member_book.html")


class MembersListView(ListView):
    model = Member
    template_name = "library/members/members.html"
    context_object_name = "members"
    paginate_by = 6

    users = User.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(user__first_name__icontains=search_query)
            )

        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get(
            "search", ""
        )  # Pass the search query back to the template
        context["users"] = self.users
        return context


class MembersBooksListView(ListView):
    model = BorrowTransaction
    template_name = "library/members/member_details.html"
    context_object_name = "borrowings"
    paginate_by = 8

    member = Member.objects.all()
    books = Book.objects.all()

    def get_queryset(self):
        member_id = self.kwargs["id"]
        queryset = super().get_queryset().filter(member_id=member_id)
        search_query = self.request.GET.get("search", "")

        self.member = Member.objects.get(id=member_id)

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) | Q(book__title__icontains=search_query)
            )

        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get(
            "search", ""
        )  # Pass the search query back to the template
        context["member"] = self.member
        context["books"] = self.books
        return context


def new_member(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        role = request.POST.get("role")

        Member.objects.create(user_id=user_id, role=role)
        return redirect("members")
    return render(request, "library/members/new_member.html")


def deactivate_member(request):
    if request.method == "POST":
        member_id = request.POST.get("member_id")
        member = Member.objects.get(id=member_id)
        member.active = False
        member.save()
        return redirect("members")
    return render(request, "library/members/deactivate_member.html")


def reactivate_member(request):
    if request.method == "POST":
        member_id = request.POST.get("member_id")
        member = Member.objects.get(id=member_id)
        member.active = True
        member.save()
        return redirect("members")
    return render(request, "library/members/reactivate_member.html")


class BooksIssuedListView(ListView):
    model = BorrowTransaction
    template_name = "library/borrowing/books_issued.html"
    context_object_name = "borrowings"
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(member__user__first_name__icontains=search_query)
                | Q(book__title__icontains=search_query)
            )

        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get(
            "search", ""
        )  # Pass the search query back to the template
        return context


def return_issued_book(request):
    if request.method == "POST":
        borrowing_id = request.POST.get("borrowing_id")

        borrowing = BorrowTransaction.objects.get(id=borrowing_id)
        borrowing.status = "Returned"
        borrowing.return_date = date_today
        borrowing.save()

        if borrowing.is_overdue:
            Fine.objects.create(borrow_transaction=borrowing)
            return redirect("issued-books")
        return redirect("issued-books")
    return render(request, "library/borrowing/return_book.html")


def mark_issued_book_as_lost(request):
    if request.method == "POST":
        borrowing_id = request.POST.get("borrowing_id")

        borrowing = BorrowTransaction.objects.get(id=borrowing_id)
        borrowing.status = "Lost"
        borrowing.save()

        Fine.objects.create(borrow_transaction=borrowing)
        return redirect("issued-books")
    return render(request, "library/borrowing/lost_book.html")


def reset_borrowed_book(request):
    if request.method == "POST":
        borrowing_id = request.POST.get("borrowing_id")

        borrowing = BorrowTransaction.objects.get(id=borrowing_id)
        borrowing.status = "Pending Return"
        borrowing.save()

        fines = Fine.objects.filter(borrow_transaction=borrowing)
        fines.delete()
        return redirect("issued-books")
    return render(request, "library/borrowing/reset_borrowing.html")


class BorrowingFinesListView(ListView):
    model = Fine
    template_name = "library/fines/fines.html"
    context_object_name = "fines"
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(
                    borrowing_transaction__member__user__first_name__icontains=search_query
                )
                | Q(borrowing_transaction__book__title__icontains=search_query)
            )

        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get(
            "search", ""
        )  # Pass the search query back to the template
        return context


@transaction.atomic
def request_fine_payment(request):
    if request.method == "POST":
        fine_id = request.POST.get("fine_id")

        fine = Fine.objects.get(id=fine_id)

        LibraryFinePayment.objects.create(
            member=fine.borrow_transaction.member,
            fine=fine,
            amount=fine.calculated_fine,
            paid=False,
        )

        fine.paid = False
        fine.save()

        return redirect("borrowing-fines")
    return render(request, "library/fines/request_fine_payment.html")
