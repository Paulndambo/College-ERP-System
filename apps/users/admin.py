from django.contrib import admin

from apps.users.models import User


# Register your models here.
@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "username", "email", "phone_number", "gender", "role")
    list_filter = ("role", "gender")
