from django.contrib import admin



from .models import Hostel,  HostelRoom, Booking


# Register your models here.
@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "rooms", "capacity", "gender", "room_cost")
    list_filter = ("gender","room_cost")
    
@admin.register(HostelRoom)
class HostelRoomAdmin(admin.ModelAdmin):
    list_display = ("id", "hostel", "room_number", "room_capacity", "students_assigned", "status", "occupancy", "fully_occupied")
    list_filter = ("hostel",)
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "hostel_room", "status")
    list_filter = ("hostel_room",)
    
    
