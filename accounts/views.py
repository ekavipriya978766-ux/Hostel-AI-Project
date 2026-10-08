from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .forms import RegistrationForm, StyledAuthenticationForm
from .models import User


class RoleAwareLoginView(LoginView):
    """Same login form for everyone; the role decides where they land."""
    template_name = "registration/login.html"
    authentication_form = StyledAuthenticationForm


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("accounts:redirect_after_login")
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def redirect_after_login(request):
    """
    Single entry point every login redirects to. Sends each role to its
    own dashboard, implementing the role-based login system.
    """
    role = request.user.role
    mapping = {
        User.Role.STUDENT: "complaints:student_dashboard",
        User.Role.WARDEN: "complaints:warden_dashboard",
        User.Role.MANAGEMENT: "complaints:management_dashboard",
        User.Role.PARENT: "complaints:parent_dashboard",
        User.Role.ADMIN: "complaints:management_dashboard",
    }
    return redirect(mapping.get(role, "complaints:student_dashboard"))
