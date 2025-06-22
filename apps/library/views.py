from apps.core.base_api_error_exceptions.base_exceptions import CustomAPIException
from apps.library.filters import (
    BookFilter,
    BorrowTransactionFilter,
    FineFilter,
    MemberFilter,
)
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.exceptions import ValidationError
from services.constants import ALL_ROLES, ALL_STAFF_ROLES, ROLE_STUDENT
from services.permissions import HasUserRole
from .models import Book, BorrowTransaction, Fine, Member
from apps.library.serializers import (
    BookCreateSerializer,
    BookListSerializer,
    BorrowTransactionCreateSerializer,
    BorrowTransactionListSerializer,
    BorrowTransactionUpdateSerializer,
    FineCreateSerializer,
    FineListSerializer,
    FinePaymentRequestSerializer,
    FineUpdateSerializer,
    LibraryFinePaymentSerializer,
    MemberCreateSerializer,
    MemberDeactivateSerializer,
    MemberListSerializer,
    MemberReactivateSerializer,
)
from apps.users.models import User
from apps.students.models import Student
from apps.staff.models import Staff


class MemberListAPIView(generics.ListAPIView):
    """API view for listing all members"""

    queryset = Member.objects.all().select_related("user")
    serializer_class = MemberListSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    filter_backends = [DjangoFilterBackend]
    filterset_class = MemberFilter
    pagination_class = None

    def get_queryset(self):
        return Member.objects.all().order_by("-created_on")

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            members = self.get_queryset()
            members = self.filter_queryset(members)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_members = paginator.paginate_queryset(members, request)
                serializer = self.get_serializer(paginated_members, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(members, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MemberCreateAPIView(generics.CreateAPIView):
    """API view for creating a new member"""

    serializer_class = MemberCreateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES

    def create(self, request, *args, **kwargs):
        try:

            serializer = self.get_serializer(data=request.data)

            serializer.is_valid(raise_exception=True)

            self.perform_create(serializer)

            return Response(
                {"message": "Member created successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            import traceback

            traceback.print_exc()
            raise


class MemberUpdateAPIView(generics.RetrieveUpdateAPIView):
    """API view for updating a member"""

    queryset = Member.objects.all()
    serializer_class = MemberCreateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    lookup_field = "pk"
    http_method_names = ["patch", "put"]


class MemberDeactivateView(generics.UpdateAPIView):
    """View for deactivating members"""

    queryset = Member.objects.all()
    serializer_class = MemberDeactivateSerializer
    lookup_field = "pk"
    http_method_names = ["patch", "put"]


class MemberReactivateView(generics.UpdateAPIView):
    """View for reactivating members"""

    queryset = Member.objects.all()
    serializer_class = MemberReactivateSerializer
    lookup_field = "pk"
    http_method_names = ["patch", "put"]


class MemberDetailAPIView(generics.RetrieveAPIView):
    """API view for retrieving a single member"""

    queryset = Member.objects.all().select_related("user")
    serializer_class = MemberListSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    lookup_field = "pk"


class BookCreateAPIView(generics.CreateAPIView):
    """API view for creating a new book"""

    serializer_class = BookCreateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES

    def create(self, request, *args, **kwargs):
        try:

            serializer = self.get_serializer(data=request.data)

            serializer.is_valid(raise_exception=True)

            self.perform_create(serializer)

            return Response(
                {"message": "Book added successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            import traceback

            traceback.print_exc()
            raise


class BookUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookCreateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    lookup_field = "pk"
    http_method_names = ["patch", "put"]


class BookListAPIView(generics.ListAPIView):
    """API view for listing all books"""

    queryset = Book.objects.all().order_by("-created_on")
    serializer_class = BookListSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookFilter
    pagination_class = None

    def get_queryset(self):
        return Book.objects.all().order_by("-created_on")

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            books = self.get_queryset()
            books = self.filter_queryset(books)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_books = paginator.paginate_queryset(books, request)
                serializer = self.get_serializer(paginated_books, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(books, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BookDetailAPIView(generics.RetrieveAPIView):
    """API view for retrieving a single book"""

    queryset = Book.objects.all()
    serializer_class = BookListSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    lookup_field = "pk"


class BorrowTransactionCreateView(generics.CreateAPIView):
    """Create a new borrow transaction."""

    queryset = BorrowTransaction.objects.all()
    serializer_class = BorrowTransactionCreateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES

    def perform_create(self, serializer):
        """Set the current user as issued_by when creating a borrow transaction"""
        serializer.save(issued_by=self.request.user)

    def create(self, request, *args, **kwargs):
        """Custom create method with custom response format"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            {"message": "Book borrowed successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class BorrowTransactionListView(generics.ListAPIView):
    """
    List all borrow transactions with filtering options.
    """

    queryset = BorrowTransaction.objects.all()
    serializer_class = BorrowTransactionListSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    filter_backends = [DjangoFilterBackend]
    filterset_class = BorrowTransactionFilter
    pagination_class = None

    def get_queryset(self):
        return BorrowTransaction.objects.all().order_by("-created_on")

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            borrow_transactions = self.get_queryset()
            borrow_transactions = self.filter_queryset(borrow_transactions)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_borrow_transactions = paginator.paginate_queryset(
                    borrow_transactions, request
                )
                serializer = self.get_serializer(
                    paginated_borrow_transactions, many=True
                )
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(borrow_transactions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BorrowTransactionUpdateView(generics.UpdateAPIView):
    """Update a borrow transaction (mainly for returning books)."""

    queryset = BorrowTransaction.objects.all()
    serializer_class = BorrowTransactionUpdateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    look_up_field = "pk"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_status = instance.status
        partial = kwargs.pop("partial", False)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data.get("status", old_status)
        self.perform_update(serializer)

        if new_status in ["Returned", "Lost"] and old_status not in [
            "Returned",
            "Lost",
        ]:
            updated_instance = self.get_object()

            if updated_instance.is_overdue() or new_status == "Lost":
                fine, created = Fine.objects.get_or_create(
                    borrow_transaction=updated_instance,
                    defaults={"fine_per_day": 0.50, "paid": False},
                )
                fine.save()

        return Response(
            {
                "message": "Borrowing record updated successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class BorrowedBookTransactionDetailAPIView(generics.RetrieveAPIView):
    """API view for retrieving a single borrow record"""

    queryset = BorrowTransaction.objects.all()
    serializer_class = BorrowTransactionListSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    lookup_field = "pk"


class FineCreateView(generics.CreateAPIView):

    queryset = Fine.objects.all()
    serializer_class = FineCreateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES

    def create(self, request, *args, **kwargs):
        """Custom create method with validation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transaction = serializer.validated_data.get("transaction")
        if Fine.objects.filter(transaction=transaction).exists():
            return Response(
                {"error": "A fine already exists for this book."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not transaction.is_overdue and transaction.status != "Lost":
            return Response(
                {"error": "Cannot create fine for non-overdue, non-lost books."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            {"message": "Fine created successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class FineListView(generics.ListAPIView):
    """
    List all fines with filtering options.
    """

    queryset = Fine.objects.all()
    serializer_class = FineListSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    filter_backends = [DjangoFilterBackend]
    filterset_class = FineFilter
    pagination_class = None

    def get_queryset(self):
        return Fine.objects.all().order_by("-created_on")

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            fines = self.get_queryset()
            fines = self.filter_queryset(fines)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_fines = paginator.paginate_queryset(fines, request)
                serializer = self.get_serializer(paginated_fines, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = self.get_serializer(fines, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FineUpdateView(generics.UpdateAPIView):
    """
    Update a fine (mainly for marking as paid).
    """

    queryset = Fine.objects.all()
    serializer_class = FineUpdateSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES

    def update(self, request, *args, **kwargs):
        """Custom update method"""
        instance = self.get_object()
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        return Response(
            {"message": "Fine updated successfully", "data": serializer.data}
        )


class FinePaymentRequestView(generics.CreateAPIView):
    serializer_class = FinePaymentRequestSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_request = serializer.save()

        output_serializer = LibraryFinePaymentSerializer(payment_request)

        return Response(
            {
                "message": "Fine payment request created successfully",
                "data": {
                    "payment_request": output_serializer.data,
                    "member": payment_request.member.user.first_name,
                    "amount": str(payment_request.amount),
                    "status": "requested",
                },
            },
            status=status.HTTP_201_CREATED,
        )
