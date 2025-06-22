from apps.hostels.filters import BookingFilter, HostelFilter, HostelRoomFilter
from apps.students.filters import StudentFilter
from apps.students.models import Student
from apps.students.serializers import StudentListSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import models
from rest_framework.pagination import PageNumberPagination
from services.constants import ALL_ROLES, ALL_STAFF_ROLES, ROLE_STUDENT
from services.permissions import HasUserRole
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.base_api_error_exceptions.base_exceptions import CustomAPIException

from .models import Hostel, HostelRoom, Booking
from .serializers import (
    AddStudentToRoomSerializer,
    HostelListSerializer,
    HostelCreateAndUpdateSerializer,
    HostelRoomDeleteSerializer,
    HostelRoomListSerializer,
    CreateAndUpdateHostelRoomSerializer,
    BookingListSerializer,
    CreateAndUpdateBookingSerializer,
    RemoveStudentFromRoomSerializer,
    UpdateBookingSerializer,
    UpdateStudentRoomSerializer,
)

# ========== HOSTEL VIEWS ==========


class HostelListView(generics.ListAPIView):
    """List all hostels"""

    queryset = Hostel.objects.all()
    serializer_class = HostelListSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    filter_backends = [DjangoFilterBackend]
    filterset_class = HostelFilter

    def get_queryset(self):
        return Hostel.objects.all().order_by("-created_on")
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            queryset = self.filter_queryset(queryset)
            
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_queryset = paginator.paginate_queryset(queryset, request)
                
                hostels_serializer = self.get_serializer(paginated_queryset, many=True)
                hostels_data = hostels_serializer.data
                return paginator.get_paginated_response(hostels_data)
                
            
            hostels_serializer = self.get_serializer(queryset, many=True)
            hostels_data = hostels_serializer.data
            return Response(hostels_data,
                status=status.HTTP_200_OK,
            )

           
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HostelCreateView(generics.CreateAPIView):
    """Create a new hostel"""

    queryset = Hostel.objects.all()
    serializer_class = HostelCreateAndUpdateSerializer


class HostelDetailView(generics.RetrieveAPIView):
    """Retrieve a specific hostel"""

    queryset = Hostel.objects.all()
    serializer_class = HostelListSerializer


class HostelUpdateView(generics.UpdateAPIView):
    """Update a specific hostel"""

    queryset = Hostel.objects.all()
    serializer_class = HostelCreateAndUpdateSerializer


class HostelDeleteView(generics.DestroyAPIView):
    """Delete a specific hostel"""

    queryset = Hostel.objects.all()



class HostelRoomListView(generics.ListAPIView):
    """List all hostel rooms"""

    queryset = HostelRoom.objects.all()
    serializer_class = HostelRoomListSerializer


class HostelRoomCreateView(generics.CreateAPIView):
    """Create a new hostel room"""

    queryset = HostelRoom.objects.all()
    serializer_class = CreateAndUpdateHostelRoomSerializer


class HostelRoomDetailView(generics.RetrieveAPIView):
    """Retrieve a specific hostel room"""

    queryset = HostelRoom.objects.all()
    serializer_class = HostelRoomListSerializer


class HostelRoomUpdateView(generics.UpdateAPIView):
    """Update a specific hostel room"""

    queryset = HostelRoom.objects.all()
    serializer_class = CreateAndUpdateHostelRoomSerializer




class AvailableRoomsListView(generics.ListAPIView):
    """List all available rooms (not fully booked)"""

    serializer_class = HostelRoomListSerializer

    def get_queryset(self):
        return HostelRoom.objects.filter(
            students_assigned__lt=models.F("room_capacity")
        )


class HostelRoomDeleteAPIView(generics.RetrieveDestroyAPIView):
    queryset = HostelRoom.objects.all()
    serializer_class = HostelRoomDeleteSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    lookup_field = "pk"
    http_method_names = ["delete"]

    def delete(self, request, *args, **kwargs):
        room = self.get_object()
        serializer = self.get_serializer(instance=room, data=request.data)
        serializer.is_valid(raise_exception=True)
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# ========== BOOKING VIEWS ==========


class RoomBookingsView(generics.ListAPIView):

    
    serializer_class = BookingListSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookingFilter
    pagination_class = None  
    
    def get_queryset(self):
        return Booking.objects.select_related(
            'student', 'hostel_room', 'student__user'
        ).order_by("-created_on")
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            queryset = self.filter_queryset(queryset)
            
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_queryset = paginator.paginate_queryset(queryset, request)
                
                bookings_serializer = self.get_serializer(paginated_queryset, many=True)
                bookings_data = bookings_serializer.data
                return paginator.get_paginated_response(bookings_data)
                
            
            bookings_serializer = self.get_serializer(queryset, many=True)
            bookings = bookings_serializer.data
            return Response(bookings,
                status=status.HTTP_200_OK,
            )

           
        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BookingCreateView(generics.CreateAPIView):
    """Create a new booking"""

    queryset = Booking.objects.all()
    serializer_class = CreateAndUpdateBookingSerializer


class BookingDetailView(generics.RetrieveAPIView):
    """Retrieve a specific booking"""

    queryset = Booking.objects.all()
    serializer_class = BookingListSerializer
    look_up_field = "pk"


class BookingUpdateView(generics.UpdateAPIView):
    """Update a specific booking (for basic fields like hostel_room, student)"""

    queryset = Booking.objects.all()
    serializer_class = UpdateBookingSerializer
    look_up_field = "pk"


class BookingDeleteView(generics.DestroyAPIView):
    """Delete a specific booking"""

    queryset = Booking.objects.all()
    look_up_field = "pk"
class AddStudentToRoomView(generics.CreateAPIView):
    """Add student to a hostel room"""
    serializer_class = AddStudentToRoomSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        
        return Response({
            'message': 'Student successfully added to room',
            'student_id': student.id,
            'student_name': f"{student.user.first_name} {student.user.last_name}",
            'room_number': student.hostel_room.room_number,
            'room_occupancy': f"{student.hostel_room.students_assigned}/{student.hostel_room.room_capacity}"
        })

class RemoveStudentFromRoomView(generics.CreateAPIView):
    """Remove student from hostel room"""
    serializer_class = RemoveStudentFromRoomSerializer
    def post(self, request, *args, **kwargs):
        serializer = RemoveStudentFromRoomSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.remove_student() 
            return Response(
                {"message": "Student removed successfully"}, 
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateStudentRoomView(generics.CreateAPIView):
    """Move student to a different room"""
    serializer_class = UpdateStudentRoomSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        
        return Response({
            'message': 'Student successfully moved to new room',
            'student_id': student.id,
            'student_name': f"{student.user.first_name} {student.user.last_name}",
            'new_room_number': student.hostel_room.room_number,
            'new_room_occupancy': f"{student.hostel_room.students_assigned}/{student.hostel_room.room_capacity}"
        })

class ConfirmBookingView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = UpdateBookingSerializer
    lookup_field = 'pk'  

    def update(self, request, *args, **kwargs):
        partial = kwargs.get('partial', False)
        instance = self.get_object()
        print("instance", instance)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        response_serializer = BookingListSerializer(booking)
        return Response(
            {
                "message": "Booking Updated successfully",
                "booking": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class HostelRoomsByHostelView(generics.ListAPIView):
    """List all rooms for a specific hostel"""

    serializer_class = HostelRoomListSerializer
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    filter_backends = [DjangoFilterBackend]
    filterset_class = HostelRoomFilter
    pagination_class = None
    def get_queryset(self):
        hostel_id = self.kwargs["hostel_id"]
        
        return HostelRoom.objects.filter(hostel_id=hostel_id).order_by("-created_on")
    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def list(self, request, *args, **kwargs):
        try:
            hostel_id = self.kwargs["hostel_id"]
            hostel = Hostel.objects.get(id=hostel_id)
            hostel_data = HostelListSerializer(hostel).data
            queryset = self.get_queryset()
            queryset = self.filter_queryset(queryset)
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_queryset = paginator.paginate_queryset(queryset, request)
                
                rooms_serializer = self.get_serializer(paginated_queryset, many=True)
                rooms_data = rooms_serializer.data
                return paginator.get_paginated_response({
                    "hostel": hostel_data,
                    "rooms": rooms_data,
                })
            
            rooms_serializer = self.get_serializer(queryset, many=True)
            rooms_data = rooms_serializer.data

            return Response(
                {
                    "hostel": hostel_data,
                    "rooms": rooms_data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RoomOccupantsView(generics.ListAPIView):
    """Get all occupants (students) for a specific room"""
    
    serializer_class = StudentListSerializer  
    permission_classes = [HasUserRole]
    allowed_roles = ALL_STAFF_ROLES
    filter_backends = [DjangoFilterBackend]
    filterset_class = StudentFilter  
    pagination_class = None  
    
    def get_queryset(self):
        room_id = self.kwargs["room_id"]
        return Student.objects.filter(
            hostel_room=room_id
        ).select_related('user', 'hostel_room', 'programme', 'cohort', 'campus').order_by("-created_on")
    
    def list(self, request, *args, **kwargs):
        try:
            room_id = self.kwargs["room_id"]
            room = HostelRoom.objects.get(id=room_id)
            room_data = HostelRoomListSerializer(room).data
            
           
            base_queryset = self.get_queryset()
            
            
            actual_occupants_count = base_queryset.count()
            available_spots = room.room_capacity - actual_occupants_count
            
            
            filtered_queryset = self.filter_queryset(base_queryset)
            
            page = self.request.query_params.get("page", None)
            if page:
                self.pagination_class = PageNumberPagination
                paginator = self.pagination_class()
                paginated_queryset = paginator.paginate_queryset(filtered_queryset, request)
                
                occupants_serializer = self.get_serializer(paginated_queryset, many=True)
                occupants_data = occupants_serializer.data
                return paginator.get_paginated_response({
                    "room": room_data,
                    "occupants": occupants_data,
                    "available_spots": available_spots,
                    "total_occupants": actual_occupants_count,  
                })
            
            occupants_serializer = self.get_serializer(filtered_queryset, many=True)
            occupants = occupants_serializer.data

            return Response(
                {
                    "room": room_data,
                    "occupants": occupants,
                    "available_spots": available_spots,
                    "total_occupants": actual_occupants_count, 
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            raise CustomAPIException(
                message=str(exc), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
