import django_filters
from django.db.models import Q
from .models import Book, BorrowTransaction, Fine, Member




class BookFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_by_all', label='Search')

    class Meta:
        model = Book
        fields = ['search']  

    def filter_by_all(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(author__icontains=value) |
            Q(isbn__icontains=value)
        )
class MemberFilter(django_filters.FilterSet):
    phone_no = django_filters.CharFilter(field_name='user__phone_number', lookup_expr='icontains')

    class Meta:
        model = Member
        fields = ['phone_no']  


class BorrowTransactionFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_by_all', label='Search')
    status = django_filters.ChoiceFilter(
        choices=BorrowTransaction._meta.get_field('status').choices,
        label='Status'
    )

    class Meta:
        model = BorrowTransaction
        fields = ['search', 'status']

    def filter_by_all(self, queryset, name, value):
        """
        Search across the most commonly searched fields
        """
        return queryset.filter(
            Q(book__title__icontains=value) |
            Q(book__author__icontains=value) |
            Q(member__user__first_name__icontains=value) |
            Q(member__user__last_name__icontains=value) |
            Q(member__user__phone_number__icontains=value)
        ).distinct()
        
class FineFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_by_all', label='Search')
    paid = django_filters.BooleanFilter(label='Paid Status')

    class Meta:
        model = Fine
        fields = ['search', 'paid']

    def filter_by_all(self, queryset, name, value):
        """
        Search across the most commonly searched fields for fines
        """
        return queryset.filter(
            Q(borrow_transaction__book__title__icontains=value) |
            Q(borrow_transaction__book__author__icontains=value) |
            Q(borrow_transaction__member__user__first_name__icontains=value) |
            Q(borrow_transaction__member__user__last_name__icontains=value) |
            Q(borrow_transaction__member__user__phone_number__icontains=value) |
            Q(calculated_fine__icontains=value)
        ).distinct()