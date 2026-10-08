from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class HostelUserAdmin(UserAdmin):
    """Gives the Admin role full CRUD over every user via /admin/."""

    list_display = ("username", "first_name", "last_name", "role", "room_number", "department", "is_active")
    list_filter = ("role", "department", "is_active")
    search_fields = ("username", "first_name", "last_name", "email", "room_number")

    fieldsets = UserAdmin.fieldsets + (
        ("Hostel AI Role Info", {
            "fields": ("role", "phone_number", "room_number", "department", "parent"),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Hostel AI Role Info", {
            "fields": ("role", "phone_number", "room_number", "department", "parent"),
        }),
    )
