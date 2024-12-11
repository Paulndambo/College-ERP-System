from django.urls import path
from apps.hostels.views import (
    BookingsListView,
    book_hostel,
    bookings_home,
    hostels,
    hostel_details,
    new_hostel,
    edit_hostel,
    delete_hostel,
    HostelRoomsListView,
    new_room,
    new_hostel_room,
    edit_room,
    delete_room,
    room_occupants,
    add_occupant,
    remove_occupant,
)

urlpatterns = [
    path("", hostels, name="hostels"),
    path("<int:hostel_id>/details/", hostel_details, name="hostel-details"),
    path("new-hostel/", new_hostel, name="new-hostel"),
    path("edit-hostel/", edit_hostel, name="edit-hostel"),
    path("delete-hostel/", delete_hostel, name="delete-hostel"),
    path("bookings/", BookingsListView.as_view(), name="bookings"),
    path("hostel-booking/", bookings_home, name="hostel-booking"),
    path("book-hostel/", book_hostel, name="book-hostel"),
    path("hostel-rooms/", HostelRoomsListView.as_view(), name="hostel-rooms"),
    path("new-hostel-room/", new_room, name="new-hostel-room"),
    path("create-hostel-room/", new_hostel_room, name="create-hostel-room"),
    path("edit-hostel-room/", edit_room, name="edit-hostel-room"),
    path("delete-hostel-room/", delete_room, name="delete-hostel-room"),
    path(
        "hostel-rooms/<int:room_id>/occupants/", room_occupants, name="room-occupants"
    ),
    path("add-occupant/", add_occupant, name="add-occupant"),
    path("remove-occupant/", remove_occupant, name="remove-occupant"),
]
