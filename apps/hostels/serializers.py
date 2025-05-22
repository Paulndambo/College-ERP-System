from rest_framework import serializers
from .models import Hostel, HostelRoom, Booking
from apps.core.serializers import CampusListSerializer


class HostelSerializer(serializers.ModelSerializer):
    campus = CampusListSerializer()
    class Meta:
        model = Hostel
        fields = "__all__"
        
class HostelRoomSerializer(serializers.ModelSerializer):
    hostel = HostelSerializer()
    class Meta:
        model = HostelRoom
        fields = "__all__"
        
class BookingSerializer(serializers.ModelSerializer):
    hostel_room = HostelRoomSerializer()
    class Meta:
        model = Booking
        fields = "__all__"
