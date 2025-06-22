# urls.py for hostels app

from django.urls import path
from . import views

urlpatterns = [
    # ========== HOSTEL URLS ==========
    path('list/', views.HostelListView.as_view(), name='hostel-list'),
    path('create/', views.HostelCreateView.as_view(), name='hostel-create'),
    path('details/<int:pk>/', views.HostelDetailView.as_view(), name='hostel-detail'),
    path('update/<int:pk>/', views.HostelUpdateView.as_view(), name='hostel-update'),
    path('delete/<int:pk>/', views.HostelDeleteView.as_view(), name='hostel-delete'),
    
    # ========== HOSTEL ROOM URLS ==========
    path('rooms/list', views.HostelRoomListView.as_view(), name='room-list'),
    path('rooms/create/', views.HostelRoomCreateView.as_view(), name='room-create'),
    path('rooms-details/<int:pk>/', views.HostelRoomDetailView.as_view(), name='room-detail'),
    path('rooms/<int:pk>/update/', views.HostelRoomUpdateView.as_view(), name='room-update'),
    path('rooms/<int:pk>/delete/', views.HostelRoomDeleteAPIView.as_view(), name='room-delete'),
    path('rooms/available/', views.AvailableRoomsListView.as_view(), name='available-rooms'),
    path('<int:hostel_id>/rooms/', views.HostelRoomsByHostelView.as_view(), name='hostel-rooms'),
    path('rooms/<int:room_id>/occupants/', views.RoomOccupantsView.as_view(), name='room-occupants'),
    # ========== BOOKING URLS ==========
    path('bookings/', views.RoomBookingsView.as_view(), name='booking-list'),
    path('bookings/create/', views.BookingCreateView.as_view(), name='booking-create'),
    path('bookings-details/<int:pk>/', views.BookingDetailView.as_view(), name='booking-detail'),
    path('bookings/<int:pk>/update/', views.BookingUpdateView.as_view(), name='booking-update'),
    path('bookings/<int:pk>/delete/', views.BookingDeleteView.as_view(), name='booking-delete'),
    
    # ========== BOOKING CONFIRMATION ==========
    path('bookings/<int:pk>/confirm-or-cancel/', views.ConfirmBookingView.as_view(), name='confirm-booking'),
    # path('students/<int:student_id>/booking/', views.StudentBookingView.as_view(), name='student-booking'),

     # Add student to room
    path('occupants/create/', views.AddStudentToRoomView.as_view(), name='add-student-to-room'),
    
    # Remove student from room
    path('occupants/remove/', views.RemoveStudentFromRoomView.as_view(), name='remove-student-from-room'),
    
    # Move student to different room
    path('occupants/update/', views.UpdateStudentRoomView.as_view(), name='update-student-room'),

]