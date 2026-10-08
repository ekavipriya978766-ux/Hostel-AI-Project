from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with a `role` field driving the whole role-based
    login/dashboard system: Student, Warden, Management, Parent, Admin.
    """

    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        WARDEN = "warden", "Warden"
        MANAGEMENT = "management", "Management"
        PARENT = "parent", "Parent"
        ADMIN = "admin", "Admin"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)

    phone_number = models.CharField(max_length=15, blank=True)

    # Students only
    room_number = models.CharField(
        max_length=10, blank=True,
        help_text="Hostel room number. Applicable to students.",
    )
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="children",
        limit_choices_to={"role": "parent"},
        help_text="Link this student to a parent account.",
    )

    # Wardens only - which internal department this warden handles.
    # Complaints are auto-routed to the warden whose department matches the
    # AI-detected department of the complaint.
    department = models.CharField(
        max_length=30, blank=True,
        help_text="Department this warden is responsible for (e.g. Electrical, Plumbing).",
    )

    def save(self, *args, **kwargs):
        # Keep Django admin access in sync with the Admin role so the
        # "Admin -> all access with CRUD" requirement works via /admin/.
        if self.role == self.Role.ADMIN:
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    # --- convenience helpers used heavily in views/templates -------------
    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_warden(self):
        return self.role == self.Role.WARDEN

    @property
    def is_management(self):
        return self.role == self.Role.MANAGEMENT

    @property
    def is_parent_role(self):
        return self.role == self.Role.PARENT

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN
