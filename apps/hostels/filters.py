import django_filters
from django.db.models import Q
from .models import Hostel, HostelRoom, Booking



class HostelFilter(django_filters.FilterSet):
    name =  django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    campus = django_filters.NumberFilter(field_name='campus_id')

    class Meta:
        model = Hostel
        fields = ['name', 'campus']  
        
        
class HostelRoomFilter(django_filters.FilterSet):
    room_no =  django_filters.CharFilter(field_name='room_number', lookup_expr='icontains')
    class Meta:
        model = HostelRoom
        fields = ['room_no']  

   
class BookingFilter(django_filters.FilterSet):
    reg_no = django_filters.CharFilter(field_name='student__registration_number', lookup_expr='icontains')
    status = django_filters.ChoiceFilter(
        choices=Booking._meta.get_field('status').choices,
        label='Status'
    )
    hostel_room = django_filters.NumberFilter(field_name='hostel_room_id')
    hostel = django_filters.NumberFilter(field_name='hostel_room__hostel_id')
    class Meta:
        model = Booking
        fields = ['status', 'reg_no', 'hostel_room', 'hostel']  