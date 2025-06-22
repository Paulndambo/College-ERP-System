from apps.finance.models import LibraryFinePayment
from apps.users.serializers import UserSerializer
from rest_framework import serializers
from django.utils import timezone
from apps.library.models import Book, Member, BorrowTransaction, Fine
from apps.users.models import User
from apps.students.models import Student
from apps.staff.models import Staff

from datetime import date

# ==================== BOOK SERIALIZERS ====================


class BookSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "author", "isbn", "category"]


class MemberSimpleSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = ["id", "user", "role"]


class BookCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating books"""

    class Meta:
        model = Book
        fields = [
            "title",
            "author",
            "category",
            "isbn",
            "publication_date",
            "copies_available",
            "total_copies",
            "unit_price",
        ]

    def create(self, validated_data):
        if not validated_data.get("copies_available"):
            validated_data["copies_available"] = validated_data.get("total_copies", 1)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Handle total_copies update and increment available_copies accordingly
        if "total_copies" in validated_data:
            new_total_copies = validated_data["total_copies"]
            print("new_total_copies=========", new_total_copies)
            old_total_copies = instance.total_copies
            print("old_total_copies=========", old_total_copies)

            copies_difference = new_total_copies - old_total_copies
            print("copies_difference******", copies_difference)
            if "copies_available" not in validated_data:
                new_available_copies = instance.copies_available + copies_difference

                validated_data["copies_available"] = max(0, new_available_copies)
            else:
                provided_available = validated_data["copies_available"]
                if provided_available > new_total_copies:
                    raise serializers.ValidationError(
                        "Available copies cannot exceed total copies."
                    )

        return super().update(instance, validated_data)

    def validate_isbn(self, value):
        qs = Book.objects.filter(isbn=value)
        if self.instance:
            qs = qs.exclude(id=self.instance.id)
        if qs.exists():
            raise serializers.ValidationError("Book with this ISBN already exists.")
        return value


class BookListSerializer(serializers.ModelSerializer):
    """Serializer for listing books with all details"""

    issue_records = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "category",
            "isbn",
            "publication_date",
            "copies_available",
            "total_copies",
            "unit_price",
            "created_on",
            "updated_on",
            "issue_records",
        ]

    def get_issue_records(self, obj):
        transactions = BorrowTransaction.objects.filter(book=obj)
        return BorrowTransactionListSerializer(transactions, many=True).data


# ==================== MEMBER SERIALIZERS ====================


class MemberListSerializer(serializers.ModelSerializer):
    """Serializer for listing members with nested user details"""

    bookes_borrowed = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = [
            "id",
            "user",
            "role",
            "date_joined",
            "active",
            "status_text",
            "created_on",
            "updated_on",
            "bookes_borrowed",
        ]

    def get_bookes_borrowed(self, obj):
        transactions = BorrowTransaction.objects.filter(member=obj)
        return BorrowTransactionListSerializer(transactions, many=True).data

    def get_staff_number(self, obj):
        if obj.role == "Staff":
            try:
                return obj.user.staff.staff_number
            except:
                return None
        return None

    def get_registration_number(self, obj):
        if obj.role == "Student":
            try:
                return obj.user.student.registration_number
            except:
                return None
        return None

    def get_department(self, obj):
        if obj.role == "Staff":
            try:
                return (
                    obj.user.staff.department.name
                    if obj.user.staff.department
                    else None
                )
            except:
                return None
        return None

    def get_programme(self, obj):
        if obj.role == "Student":
            try:
                return (
                    obj.user.student.programme.name
                    if obj.user.student.programme
                    else None
                )
            except:
                return None
        return None


class MemberCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating members"""

    staff_number = serializers.CharField(
        required=False, allow_blank=True, write_only=True
    )
    registration_number = serializers.CharField(
        required=False, allow_blank=True, write_only=True
    )

    class Meta:
        model = Member
        fields = [
            "id",
            "user",
            "role",
            "date_joined",
            "active",
            "staff_number",
            "registration_number",
        ]
        # read_only_fields = ['id', 'user', 'role', 'date_joined', 'active']
        extra_kwargs = {
            "active": {"required": False},
            "role": {"required": False},
            "staff_number": {"required": False},
            "registration_number": {"required": False},
            "date_joined": {"required": False},
            "user": {"required": False},
        }

    def validate(self, data):
        staff_number = data.get("staff_number", "").strip()
        registration_number = data.get("registration_number", "").strip()

        if not staff_number and not registration_number:
            raise serializers.ValidationError(
                "Either staff_number or registration_number must be provided."
            )

        if staff_number and registration_number:
            raise serializers.ValidationError(
                "Provide either staff_number or registration_number, not both."
            )
        return data

    def create(self, validated_data):
        try:

            staff_number = validated_data.pop("staff_number", "").strip()
            registration_number = validated_data.pop("registration_number", "").strip()

            user = None
            role = None

            if staff_number:
                try:
                    staff_member = Staff.objects.get(staff_number=staff_number)
                    user = staff_member.user
                    role = "Staff"
                except Staff.DoesNotExist:
                    raise serializers.ValidationError(
                        {
                            "staff_number": f"No staff member found with staff number: {staff_number}"
                        }
                    )

            elif registration_number:
                try:
                    student = Student.objects.get(
                        registration_number=registration_number
                    )
                    user = student.user
                    role = "Student"
                except Student.DoesNotExist:
                    raise serializers.ValidationError(
                        {
                            "registration_number": f"No student found with registration number: {registration_number}"
                        }
                    )

            if Member.objects.filter(user=user).exists():
                identifier = staff_number or registration_number
                user_type = "staff member" if staff_number else "student"
                raise serializers.ValidationError(
                    f"The {user_type} with identifier '{identifier}' is already a library member."
                )

            instance = Member.objects.create(user=user, role=role)

            return instance

        except Exception as e:
            import traceback

            traceback.print_exc()
            raise

    def to_representation(self, instance):
        try:
            data = {
                "id": instance.id,
                "role": instance.role,
                "active": instance.active,
            }

            if instance.user:
                data["user"] = instance.user.id

            if hasattr(instance, "date_joined") and instance.date_joined:
                data["date_joined"] = instance.date_joined.isoformat()
            return data

        except Exception as e:
            print(f"Error in to_representation: {e}")
            import traceback

            traceback.print_exc()

            return {"id": instance.id if instance else None}


class MemberDeactivateSerializer(serializers.ModelSerializer):
    """Serializer for deactivating members"""

    class Meta:
        model = Member
        fields = ["id"]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):
        """Automatically deactivate member"""
        instance.active = False
        instance.save()
        return instance

    def to_representation(self, instance):
        """Custom representation"""
        return {
            "id": instance.id,
            "active": instance.active,
            "user_id": instance.user.id,
            "user_name": f"{instance.user.first_name} {instance.user.last_name}",
            "role": instance.role,
            "date_joined": (
                instance.date_joined.isoformat() if instance.date_joined else None
            ),
        }


class MemberReactivateSerializer(serializers.ModelSerializer):
    """Serializer for reactivating members"""

    class Meta:
        model = Member
        fields = ["id"]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):
        """Automatically reactivate member"""
        instance.active = True
        instance.save()
        return instance

    def to_representation(self, instance):
        """Custom representation"""
        return {
            "id": instance.id,
            "active": instance.active,
            "user_id": instance.user.id,
            "user_name": f"{instance.user.first_name} {instance.user.last_name}",
            "role": instance.role,
            "date_joined": (
                instance.date_joined.isoformat() if instance.date_joined else None
            ),
        }


# ==================== BORROW TRANSACTION SERIALIZERS ====================


class BorrowTransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating borrow transactions"""

    member = serializers.PrimaryKeyRelatedField(queryset=Member.objects.all())

    class Meta:
        model = BorrowTransaction
        fields = [
            "book",
            "copy_number",
            "member",
            "borrow_date",
            "due_date",
            "status",
            "issued_by",
        ]
        extra_kwargs = {
            "borrow_date": {"required": False},
            "issued_by": {"required": False},
            "status": {"required": False},
        }

    def validate(self, data):
        book = data.get("book")
        copy_number = data.get("copy_number")

        if book and book.copies_available <= 0:
            raise serializers.ValidationError(
                {"book": "This book is not available for borrowing."}
            )

        if book and copy_number:
            existing_transaction = BorrowTransaction.objects.filter(
                book=book, copy_number=copy_number, status="Borrowed"
            ).first()

            if existing_transaction:
                raise serializers.ValidationError(
                    {
                        "copy_number": f"Copy #{copy_number} of this book is already borrowed."
                    }
                )

        return data

    def create(self, validated_data):
        book = validated_data["book"]

        if book.copies_available > 0:
            book.copies_available -= 1
            book.save()

        return super().create(validated_data)


class BorrowTransactionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating borrow transactions (mainly for returns)"""

    class Meta:
        model = BorrowTransaction
        fields = [
            "status",
            "return_date",
        ]
        extra_kwargs = {
            "return_date": {"required": False},
        }

    def validate_status(self, value):
        """Validate status transitions"""
        if self.instance and self.instance.status == "Returned" and value != "Returned":
            raise serializers.ValidationError(
                "Cannot change status of an already returned book."
            )
        return value

    def validate(self, data):
        """Additional validation for the update"""
        status = data.get("status")
        return_date = data.get("return_date")

        if (
            status == "Returned"
            and not return_date
            and self.instance.status != "Returned"
        ):
            data["return_date"] = date.today()

        if return_date and return_date > date.today():
            raise serializers.ValidationError(
                {"return_date": "Return date cannot be in the future."}
            )

        return data

    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get("status", old_status)

        if new_status == "Returned" and old_status != "Returned":
            book = instance.book
            book.copies_available += 1
            book.save()

            if not validated_data.get("return_date"):
                validated_data["return_date"] = date.today()

        return super().update(instance, validated_data)


class BorrowTransactionListSerializer(serializers.ModelSerializer):
    """Serializer for listing borrow transactions with nested details"""

    # book = BookListSerializer(read_only=True)
    # member = MemberListSerializer(read_only=True)
    book = BookSimpleSerializer(read_only=True)
    member = MemberSimpleSerializer(read_only=True)
    issued_by = UserSerializer(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)

    class Meta:
        model = BorrowTransaction
        fields = [
            "id",
            "book",
            "copy_number",
            "member",
            "borrow_date",
            "due_date",
            "return_date",
            "status",
            "issued_by",
            "is_overdue",
            "days_overdue",
            "created_on",
            "updated_on",
        ]

    # def update(self, instance, validated_data):
    #     if "status" in validated_data and validated_data["status"] == "Returned":
    #         if not validated_data.get("return_date"):
    #             validated_data["return_date"] = timezone.now().date()

    #         if instance.status != "Returned":
    #             instance.book.copies_available += 1
    #             instance.book.save()

    #     return super().update(instance, validated_data)


# ==================== FINE SERIALIZERS ====================


class FineCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating fines"""

    class Meta:
        model = Fine
        fields = ["borrow_transaction", "fine_per_day", "paid"]


class FineUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating fines (mainly for marking as paid)"""

    class Meta:
        model = Fine
        fields = ["paid"]  # Only allow updating the paid status

    def validate_paid(self, value):
        """Validate that we're not marking an already paid fine as unpaid"""
        if self.instance and self.instance.paid and not value:
            raise serializers.ValidationError("Cannot mark a paid fine as unpaid.")
        return value

    def update(self, instance, validated_data):
        # You might want to add logic here like recording payment timestamp
        # or updating related payment records
        return super().update(instance, validated_data)


class BorrowTransactionNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for borrow transaction in fines"""

    book = BookListSerializer(read_only=True)
    member = MemberListSerializer(read_only=True)

    class Meta:
        model = BorrowTransaction
        fields = [
            "id",
            "book",
            "member",
            "borrow_date",
            "due_date",
            "return_date",
            "status",
        ]


class FineListSerializer(serializers.ModelSerializer):
    """Serializer for listing fines with nested transaction details"""

    borrow_transaction = BorrowTransactionNestedSerializer(read_only=True)
    status_text = serializers.CharField(read_only=True)

    class Meta:
        model = Fine
        fields = [
            "id",
            "borrow_transaction",
            "fine_per_day",
            "calculated_fine",
            "paid",
            "status_text",
            "created_on",
            "updated_on",
        ]


class FinePaymentRequestSerializer(serializers.ModelSerializer):
    """Serializer for requesting fine payment"""

    fine = serializers.PrimaryKeyRelatedField(queryset=Fine.objects.all())

    class Meta:
        model = LibraryFinePayment
        fields = ["fine"]

    def validate_fine(self, value):
        """Validate that fine exists and can have payment requested"""

        fine = value

        if LibraryFinePayment.objects.filter(fine=fine).exists():
            raise serializers.ValidationError(
                "Payment request already exists for this fine."
            )

        if fine.paid:
            raise serializers.ValidationError("This fine is already paid.")

        return value

    def create(self, validated_data):
        fine = validated_data["fine"]

        payment_request = LibraryFinePayment.objects.create(
            member=fine.borrow_transaction.member,
            fine=fine,
            amount=fine.calculated_fine,
            paid=False,
        )

        # Update the fine status if needed
        fine.paid = False
        fine.save()

        return payment_request


class LibraryFinePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryFinePayment
        fields = [
            "id",
            "member",
            "fine",
            "amount",
            "paid",
            "payment_date",
            "payment_method",
            "payment_reference",
        ]
        depth = 1


# class FinePaymentRequestSerializer(serializers.ModelSerializer):
#     """Serializer for requesting fine payment"""
#     fine = serializers.PrimaryKeyRelatedField(queryset=Fine.objects.all())

#     class Meta:
#         model = LibraryFinePayment
#         fields = ["fine"]

#     def validate_fine(self, value):
#         """Validate that fine exists and can have payment requested"""
#         try:
#             fine = Fine.objects.get(id=value)
#         except Fine.DoesNotExist:
#             raise serializers.ValidationError("Fine not found.")


#         if LibraryFinePayment.objects.filter(fine=fine).exists():
#             raise serializers.ValidationError("Payment request already exists for this fine.")


#         if fine.paid:
#             raise serializers.ValidationError("This fine is already paid.")

#         return value

#     def create(self, validated_data):
#         fine_obj = validated_data['fine']
#         fine = Fine.objects.get(id=fine_obj.id)

#         payment_request = LibraryFinePayment.objects.create(
#             member=fine.borrow_transaction.member,
#             fine=fine,
#             amount=fine.calculated_fine,
#             paid=False,
#         )

#         fine.paid = False
#         fine.save()

#         return payment_request
