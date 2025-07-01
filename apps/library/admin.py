from django.contrib import admin


from .models import BorrowTransaction, Fine, Member


# Register your models here.
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role", "date_joined")
    list_filter = ("active", "role")


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "borrow_transaction",
        "calculated_fine",
        "fine_per_day",
        "paid",
        "status_text",
        "created_on",
        "updated_on",
    )
    list_filter = ("paid",)

@admin.register(BorrowTransaction)
class BorrowTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "book",
        "member",
        "borrow_date",
        "due_date",
        "return_date",
        "issued_by",
        "status",
        "copy_number",
        "days_overdue",
        "is_overdue",
        "created_on",
        "updated_on",
    )
