from apps.core.models import Campus
from apps.finance.models import Payment
from apps.students.models import Student
from django.db import transaction
from rest_framework import serializers
from .models import Hostel, HostelRoom, Booking
from apps.core.serializers import CampusListSerializer
from datetime import date


class HostelListSerializer(serializers.ModelSerializer):
    campus = CampusListSerializer()
    class Meta:
        model = Hostel
        fields = [
            "id",
            "name",
            "gender",
            "capacity",
            "rooms",
            "room_cost",
            "campus",
            "created_on",
            "updated_on",
        
        ]
class HostelCreateAndUpdateSerializer(serializers.ModelSerializer):
    campus = serializers.PrimaryKeyRelatedField(queryset=Campus.objects.all())
    class Meta:
        model = Hostel
        fields = [
            'name',
            'capacity',
            'rooms',
            'room_cost',
            'gender',
            'campus',
        ] 
        extra_kwargs = {    
            'gender': {'required': False},
            'campus': {'required': False},
        }
class HostelRoomListSerializer(serializers.ModelSerializer):
    hostel = HostelListSerializer()
    fully_occupied = serializers.SerializerMethodField()
    occupancy = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    class Meta:
        model = HostelRoom
        fields = [
            "id",
            "hostel",
            "room_number",
            "room_capacity",
            "students_assigned",
            "fully_occupied",
            "occupancy",
            "status",
        ]
    def fully_occupied(self, obj):
        return obj.fully_occupied()

    def get_occupancy(self, obj):
        return obj.occupancy()

    def get_status(self, obj):
        return obj.status()
class HostelRoomBaseSerializer(serializers.ModelSerializer):
    hostel = HostelListSerializer()
    class Meta:
        model = HostelRoom
        fields = "__all__"    
class CreateAndUpdateHostelRoomSerializer(serializers.ModelSerializer):
    hostel = serializers.PrimaryKeyRelatedField(queryset=Hostel.objects.all())
    class Meta:
        model = HostelRoom
        fields = [
            'hostel',
            'room_number',
            'room_capacity',
            'students_assigned',
            
        ]
class HostelRoomDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelRoom
        fields = []  

    def validate(self, attrs):
        room = self.instance  

        if room.students_assigned > 0:
            raise serializers.ValidationError("Cannot delete room with students assigned.")
        
        if room.booking_set.filter(status="Checked In").exists():
            raise serializers.ValidationError("Cannot delete room with bookings of status currently checked in.")

        return attrs   
        
class BookingListSerializer(serializers.ModelSerializer):
    hostel_room = HostelRoomListSerializer()
    
    class Meta:
        model = Booking
        fields = "__all__"
    def to_representation(self, instance):
        from apps.students.serializers import StudentListSerializer
        
        representation = super().to_representation(instance)
        representation['student'] = StudentListSerializer(instance.student).data
        return representation
class CreateAndUpdateBookingSerializer(serializers.ModelSerializer):
    hostel_room = serializers.PrimaryKeyRelatedField(queryset=HostelRoom.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    class Meta:
        model = Booking
        fields = [
            "hostel_room",
            "student",
            "status"
        ]
        extra_kwargs = {
            'status': {'required': False},
        }
    def create(self, validated_data):
        hostel_room = validated_data['hostel_room']
        student = validated_data['student']
        if Booking.objects.filter(student=student).exists():
            raise serializers.ValidationError("Student is already assigned to a hostel room")
        
        with transaction.atomic():
            hostel_room = HostelRoom.objects.select_for_update().get(pk=hostel_room.id)
            if hostel_room.students_assigned >= hostel_room.room_capacity:
                raise serializers.ValidationError("Room is fully booked")
            
            booking = super().create(validated_data)
           
            hostel_room.students_assigned += 1
            hostel_room.save()
            
            print(f"Booking created successfully. New students_assigned: {hostel_room.students_assigned}")
            
            return booking


class UpdateBookingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Booking
        fields = ['status']
    
    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get('status', old_status)
        
        with transaction.atomic():
            booking = super().update(instance, validated_data)
            
            if old_status == "Pending" and new_status == "Confirmed":
                self._confirm_booking(booking)
                
            elif old_status == "Pending" and new_status == "Cancelled":
                self._cancel_pending_or_confirmed_booking(booking)
                
            elif old_status == "Confirmed" and new_status == "Cancelled":
                pass
                
        return booking
    def _confirm_booking(self, booking):
        """When booking is confirmed, occupy the room"""
        try:
      
            booking.hostel_room.students_assigned += 1
            booking.hostel_room.save()
            
           
            booking.student.hostel_room = booking.hostel_room
            booking.student.save()
            
        except Exception as e:
            raise serializers.ValidationError(f"Error confirming booking: {str(e)}")
    
    def _cancel_pending_or_confirmed_booking(self, booking):
        """When confirmed booking is cancelled, free up the room"""
        try:
           
            current_count = booking.hostel_room.students_assigned
            if current_count > 0:
                booking.hostel_room.students_assigned = current_count - 1
            else:
                booking.hostel_room.students_assigned = 0
                
            booking.hostel_room.save()
            
            # Unassign room from student
            booking.student.hostel_room = None
            booking.student.save()
                
        except Exception as e:
            raise serializers.ValidationError(f"Error cancelling booking: {str(e)}")
    
    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        new_status = attrs.get('status')
        
       
        if new_status == "Confirmed" and instance:
            if instance.hostel_room.fully_occupied():
                raise serializers.ValidationError("Cannot confirm booking: Room is fully occupied")
        
        return attrs



class AddStudentToRoomSerializer(serializers.Serializer):
    """Add student to a hostel room"""
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    hostel_room = serializers.PrimaryKeyRelatedField(queryset=HostelRoom.objects.all())
    
    def validate(self, data):
        student = data['student']
        hostel_room = data['hostel_room']
        
    
        if student.hostel_room is not None:
            raise serializers.ValidationError(
                f"Student is already assigned to room {student.hostel_room.room_number}"
            )
        
        
        if hasattr(student, 'booking'):
            raise serializers.ValidationError("Student already has an active booking")
        
      
        if hostel_room.students_assigned >= hostel_room.room_capacity:
            raise serializers.ValidationError("Room is fully occupied")
        
        return data
    
    def create(self, validated_data):
        student = validated_data['student']
        hostel_room = validated_data['hostel_room']
        
        with transaction.atomic():
            hostel_room = HostelRoom.objects.select_for_update().get(pk=hostel_room.id)
            if hostel_room.students_assigned >= hostel_room.room_capacity:
                raise serializers.ValidationError("Room is fully occupied")
            
            student.hostel_room = hostel_room
            student.save()
            
            hostel_room.students_assigned += 1
            hostel_room.save()
        
        return student
class RemoveStudentFromRoomSerializer(serializers.Serializer):
    """Remove student from hostel room"""
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    
    def validate_student(self, value):
        if value.hostel_room is None:
            raise serializers.ValidationError("Student is not assigned to any room")
        return value
    
    def remove_student(self):
        """Custom method to handle student removal from room"""
        student = self.validated_data['student']
        
        with transaction.atomic():
            hostel_room = HostelRoom.objects.select_for_update().get(pk=student.hostel_room.id)
            student.hostel_room = None
            student.save()
            hostel_room.students_assigned = max(0, hostel_room.students_assigned - 1)
            hostel_room.save()
        
        return student

class UpdateStudentRoomSerializer(serializers.Serializer):
    """Move student from one room to another"""
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    hostel_room = serializers.PrimaryKeyRelatedField(queryset=HostelRoom.objects.all())
    
    def validate(self, data):
        student = data['student']
        new_room = data['hostel_room']
        
        if student.hostel_room is None:
            raise serializers.ValidationError("Student is not currently assigned to any room")
        
       
        if student.hostel_room.id == new_room.id:
            raise serializers.ValidationError("Student is already in this room")
        
       
        if new_room.students_assigned >= new_room.room_capacity:
            raise serializers.ValidationError("New room is fully occupied")
        
        return data
    
    def create(self, validated_data):
        student = validated_data['student']
        new_room = validated_data['new_hostel_room']
        
        with transaction.atomic():
         
            old_room = HostelRoom.objects.select_for_update().get(pk=student.hostel_room.id)
            new_room = HostelRoom.objects.select_for_update().get(pk=new_room.id)
            
            
            student.hostel_room = new_room
            student.save()
            
           
            old_room.students_assigned -= 1
            old_room.save()
            
            new_room.students_assigned += 1
            new_room.save()
        
        return student