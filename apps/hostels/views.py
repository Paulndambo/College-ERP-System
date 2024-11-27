from datetime import datetime, timedelta
import calendar

from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from django.db import transaction

from django.views.generic import ListView
from django.http import JsonResponse

from apps.hostels.models import Booking, Hostel, HostelRoom
from apps.core.models import Campus
from apps.students.models import Student

number_of_rooms = 4

GENDER_CHOICES = ["Male", "Female", "Mixed"]


# Create your views here.
def hostels(request):
    hostels = Hostel.objects.all().order_by("-created_on")

    if request.method == "POST":
        search_text = request.POST.get("search_text")
        hostels = Hostel.objects.filter(Q(name__icontains=search_text))

    paginator = Paginator(hostels, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    campuses = Campus.objects.all()

    context = {
        "page_obj": page_obj,
        "campuses": campuses,
        "gender_choices": GENDER_CHOICES,
    }
    return render(request, "hostels/hostels.html", context)


def hostel_details(request, hostel_id):
    hostel = Hostel.objects.get(id=hostel_id)
    rooms = HostelRoom.objects.filter(hostel_id=hostel_id).order_by("-created_on")

    if request.method == "POST":
        search_text = request.POST.get("search_text")
        rooms = HostelRoom.objects.filter(Q(room_number__icontains=search_text))

    paginator = Paginator(rooms, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"hostel": hostel, "page_obj": page_obj}
    return render(request, "hostels/hostel_details.html", context)


def new_hostel(request):
    if request.method == "POST":
        name = request.POST.get("name")
        rooms = request.POST.get("rooms")
        room_cost = request.POST.get("room_cost")
        capacity = request.POST.get("capacity")
        gender = request.POST.get("gender")
        campus = request.POST.get("campus")

        Hostel.objects.create(
            name=name,
            rooms=rooms,
            room_cost=room_cost,
            capacity=capacity,
            gender=gender,
            campus_id=campus,
        )

        return redirect("hostels")
    return render(request, "hostels/new_hostel.html")


def edit_hostel(request):
    if request.method == "POST":
        hostel_id = request.POST.get("hostel_id")
        name = request.POST.get("name")
        rooms = request.POST.get("rooms")
        room_cost = request.POST.get("room_cost")
        capacity = request.POST.get("capacity")
        gender = request.POST.get("gender")
        campus = request.POST.get("campus")

        hostel = Hostel.objects.get(id=hostel_id)
        hostel.name = name
        hostel.rooms = rooms
        hostel.room_cost = room_cost
        hostel.capacity = capacity
        hostel.gender = gender
        hostel.campus_id = campus
        hostel.save()

        return redirect("hostels")
    return render(request, "hostels/edit_hostel.html")


def delete_hostel(request):
    if request.method == "POST":
        hostel_id = request.POST.get("hostel_id")
        Hostel.objects.get(id=hostel_id).delete()
        return redirect("hostels")
    return render(request, "hostels/delete_hostel.html")


hostels_list = Hostel.objects.all()


class HostelRoomsListView(ListView):
    model = HostelRoom
    template_name = "hostels/rooms/hostel_rooms.html"
    context_object_name = "hostel-rooms"
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(room_number__icontains=search_query)
                | Q(hostel__name__icontains=search_query)
            )

        # Get sort parameter
        return queryset.order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["hostels"] = hostels_list
        return context


def room_occupants(request, room_id):
    room = HostelRoom.objects.get(id=room_id)
    room_occupants = Student.objects.filter(hostel_room=room)

    students = Student.objects.filter(
        hostel_room__isnull=True, user__gender=room.hostel.gender
    )

    context = {"occupants": room_occupants, "room": room, "students": students}
    return render(request, "hostels/rooms/room_occupants.html", context)


def add_occupant(request):
    if request.method == "POST":
        room_id = request.POST.get("room_id")
        student_id = request.POST.get("student_id")

        room = HostelRoom.objects.get(id=room_id)
        student = Student.objects.get(id=student_id)
        student.hostel_room = room
        student.save()

        room.students_assigned += 1
        room.save()

        return redirect(f"/hostels/hostel-rooms/{room_id}/occupants")
    return render(request, "hostels/rooms/add_occupant.html")


def remove_occupant(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")

        student = Student.objects.get(id=student_id)

        room = HostelRoom.objects.get(id=student.hostel_room.id)
        room.students_assigned -= 1
        room.save()

        student.hostel_room = None
        student.save()

        return redirect(f"/hostels/hostel-rooms/{room.id}/occupants")
    return render(request, "hostels/rooms/add_occupant.html")


def new_room(request):
    if request.method == "POST":
        room_number = request.POST.get("room_number")
        room_capacity = request.POST.get("room_capacity")
        hostel_id = request.POST.get("hostel_id")

        HostelRoom.objects.create(
            room_number=room_number, room_capacity=room_capacity, hostel_id=hostel_id
        )

        return redirect("hostel-rooms")
    return render(request, "hostels/rooms/new_hostel_room.html")


def new_hostel_room(request):
    if request.method == "POST":
        room_number = request.POST.get("room_number")
        room_capacity = request.POST.get("room_capacity")
        hostel_id = request.POST.get("hostel_id")

        HostelRoom.objects.create(
            room_number=room_number, room_capacity=room_capacity, hostel_id=hostel_id
        )

        return redirect(f"/hostels/{hostel_id}/details")
    return render(request, "hostels/rooms/create_hostel_room.html")


def edit_room(request):
    if request.method == "POST":
        room_id = request.POST.get("room_id")
        room_number = request.POST.get("room_number")
        room_capacity = request.POST.get("room_capacity")

        room = HostelRoom.objects.get(id=room_id)
        room.room_number = room_number
        room.room_capacity = room_capacity
        room.save()

        return redirect(f"/hostels/{room.hostel.id}/details")
    return render(request, "hostels/rooms/edit_hostel_room.html")


def delete_room(request):
    if request.method == "POST":
        room_id = request.POST.get("room_id")
        HostelRoom.objects.get(id=room_id).delete()
        return redirect(f"/hostels/{room.hostel.id}/details")
    return render(request, "hostels/rooms/delete_hostel_room.html")


class BookingsListView(ListView):
    model = Booking
    template_name = "hostels/bookings/bookings.html"
    context_object_name = "bookings"
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("search", "")

        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query)
                | Q(student__registration_number__icontains=search_query)
            )

        # Get sort parameter
        return queryset.annotate(
            is_pending=Case(
                When(
                    status="Pending", then=Value(0)
                ),  # Pending bookings are given a value of 0
                default=Value(1),  # All other statuses are given a value of 1
                output_field=IntegerField(),
            )
        ).order_by("-created_on")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        return context


def bookings_home(request):
    booking = None
    total_bookings = Booking.objects.count()
    if request.method == "POST":
        search = request.POST.get("search_text")
        if search:
            booking = Booking.objects.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(registration_number__icontains=search)
            ).first()

            if booking:
                something_found = True
                print(
                    f"Booking ID: {booking.id}, Student: {booking.first_name} {booking.last_name}"
                )

    context = {
        "can_book": True if total_bookings < number_of_rooms else False,
        "booking": booking,
    }

    print(context)

    return render(request, "hostels/bookings/bookings_home.html", context)


def book_hostel(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        registration_number = request.POST.get("registration_number")
        gender = request.POST.get("gender")
        phone_number = request.POST.get("phone_number")
        amount = request.POST.get("amount")
        mpesa_code = request.POST.get("mpesa_code")

        guardian_name = request.POST.get("guardian_name")
        guardian_phone_number = request.POST.get("guardian_phone_number")

        address = request.POST.get("address")
        city = request.POST.get("city")
        country = request.POST.get("country")

        booking = Booking.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            registration_number=registration_number,
            gender=gender,
            phone_number=phone_number,
            guardian_name=guardian_name,
            guardian_phone_number=guardian_phone_number,
            address=address,
            city=city,
            country=country,
            status="Pending",
            amount=amount,
            mpesa_code=mpesa_code,
        )

        return redirect("hostel-booking")

        messages.success(request, "Hostel booking successful.")
    return render(request, "hostels/bookings/book_hostel.html")
