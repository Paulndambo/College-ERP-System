from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.db.models import Q


# Create your views here.
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        print("****** Login Request Initiated ********")
        print(user)
        if user is not None:
            login(request, user)
            return redirect("/")
    return render(request, "accounts/login.html")


def user_logout(request):
    logout(request)
    return redirect("/")


def user_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
                return redirect("user_register")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists")
                return redirect("register")
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password
                )
                user.save()
                messages.success(request, "Account created successfully")
                return redirect("login")
        else:
            messages.error(request, "Passwords do not match")
            return redirect("register")
    return render(request, "account/register.html")
