from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class StyledAuthenticationForm(AuthenticationForm):
    """Just adds Bootstrap-ish classes; no logic changes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class RegistrationForm(UserCreationForm):
    """
    A single registration form that adapts to the selected role:
      - Student  -> room_number, optional parent link
      - Warden   -> department (which complaints get routed to them)
      - Parent   -> nothing extra (students link to them afterwards)
      - Management -> nothing extra

    NOTE: "Admin" is deliberately NOT offered here. The User model grants
    is_staff/is_superuser automatically to the Admin role, so allowing
    public self-registration as Admin would let anyone grant themselves
    full CRUD access. Create Admin accounts with
    `python manage.py createsuperuser` (or the seed_demo_data command)
    instead.
    """

    email = forms.EmailField(required=True)
    phone_number = forms.CharField(required=False, max_length=15)
    room_number = forms.CharField(required=False, max_length=10, label="Room Number")
    department = forms.ChoiceField(required=False, choices=[], label="Department (Wardens only)")
    role = forms.ChoiceField(
        choices=[c for c in User.Role.choices if c[0] != User.Role.ADMIN],
    )
    parent = forms.ModelChoiceField(
        required=False,
        queryset=User.objects.filter(role=User.Role.PARENT),
        label="Link Parent Account (optional)",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username", "first_name", "last_name", "email",
            "phone_number", "role", "room_number", "department", "parent",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.conf import settings as dj_settings
        self.fields["department"].choices = [("", "---------")] + [
            (d, d) for d in dj_settings.HOSTEL_DEPARTMENTS
        ]
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_role(self):
        role = self.cleaned_data["role"]
        if role == User.Role.ADMIN:
            raise forms.ValidationError("Admin accounts can't be self-registered.")
        return role

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get("role")
        if role == User.Role.STUDENT and not cleaned.get("room_number"):
            self.add_error("room_number", "Room number is required for students.")
        if role == User.Role.WARDEN and not cleaned.get("department"):
            self.add_error("department", "Please choose the department this warden handles.")
        return cleaned
