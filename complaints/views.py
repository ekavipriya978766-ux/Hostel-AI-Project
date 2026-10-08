import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import User
from .decorators import role_required
from .forms import ComplaintForm, StatusUpdateForm
from .models import Complaint, Notification, StatusUpdate


# ---------------------------------------------------------------------------
# STUDENT
# ---------------------------------------------------------------------------
@role_required(User.Role.STUDENT)
def student_dashboard(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.student = request.user
            complaint.save()  # pre_save signal runs AI severity + routing here
            messages.success(
                request,
                f"Complaint submitted. Predicted severity: {complaint.get_severity_display()}.",
            )
            return redirect("complaints:student_dashboard")
    else:
        form = ComplaintForm()

    my_complaints = Complaint.objects.filter(student=request.user)
    return render(request, "complaints/student_dashboard.html", {
        "form": form,
        "complaints": my_complaints,
    })


# ---------------------------------------------------------------------------
# SHARED DETAIL VIEW (permission-checked per role)
# ---------------------------------------------------------------------------
@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    user = request.user

    allowed = (
        user.is_superuser
        or complaint.student_id == user.id
        or (user.is_warden and complaint.assigned_warden_id == user.id)
        or user.is_management
        or (user.is_parent_role and complaint.student.parent_id == user.id)
    )
    if not allowed:
        messages.error(request, "You don't have access to that complaint.")
        return redirect("accounts:redirect_after_login")

    if user.id != complaint.student_id:
        complaint.mark_viewed_by(user)

    status_form = None
    if request.method == "POST" and user.is_warden and complaint.assigned_warden_id == user.id:
        status_form = StatusUpdateForm(request.POST)
        if status_form.is_valid():
            _apply_status_update(complaint, request.user, status_form.cleaned_data["status"], status_form.cleaned_data["note"])
            messages.success(request, "Status updated and everyone notified.")
            return redirect("complaints:complaint_detail", pk=pk)
    elif user.is_warden and complaint.assigned_warden_id == user.id:
        status_form = StatusUpdateForm(initial={"status": complaint.status})

    return render(request, "complaints/complaint_detail.html", {
        "complaint": complaint,
        "status_form": status_form,
        "history": complaint.status_updates.select_related("changed_by"),
    })


def _apply_status_update(complaint: Complaint, changed_by, new_status, note):
    old_status = complaint.status
    complaint.status = new_status
    if new_status == Complaint.Status.RESOLVED:
        complaint.resolved_at = timezone.now()
    complaint.save(update_fields=["status", "resolved_at", "updated_at"])

    StatusUpdate.objects.create(
        complaint=complaint, old_status=old_status, new_status=new_status,
        changed_by=changed_by, note=note,
    )

    recipients = {complaint.student}
    if complaint.student.parent_id:
        recipients.add(complaint.student.parent)
    recipients |= set(User.objects.filter(role=User.Role.MANAGEMENT, is_active=True))

    message = f"Complaint #{complaint.pk} ({complaint.title}) status changed to {complaint.get_status_display()}."
    Notification.objects.bulk_create([
        Notification(recipient=r, complaint=complaint, notif_type=Notification.NotifType.STATUS_UPDATE, message=message)
        for r in recipients
    ])


# ---------------------------------------------------------------------------
# WARDEN
# ---------------------------------------------------------------------------
@role_required(User.Role.WARDEN)
def warden_dashboard(request):
    complaints = list(Complaint.objects.filter(assigned_warden=request.user))
    for c in complaints:
        c.label_for_display = c.label_for(request.user)
    return render(request, "complaints/warden_dashboard.html", {"complaints": complaints})


# ---------------------------------------------------------------------------
# MANAGEMENT (+ admin lands here too)
# ---------------------------------------------------------------------------
@role_required(User.Role.MANAGEMENT, User.Role.ADMIN)
def management_dashboard(request):
    base_qs = Complaint.objects.select_related("student", "assigned_warden").all()

    severity_counts = dict(
        base_qs.values_list("severity").annotate(count=Count("id")).order_by()
    )
    status_counts = dict(
        base_qs.values_list("status").annotate(count=Count("id")).order_by()
    )
    total = base_qs.count()

    complaints = list(base_qs)
    for c in complaints:
        c.label_for_display = c.label_for(request.user)

    chart_data = {
        "severity": {
            "labels": ["High", "Medium", "Low"],
            "values": [
                severity_counts.get("high", 0),
                severity_counts.get("medium", 0),
                severity_counts.get("low", 0),
            ],
        },
        "status": {
            "labels": ["New", "In Progress", "Resolved"],
            "values": [
                status_counts.get("new", 0),
                status_counts.get("in_progress", 0),
                status_counts.get("resolved", 0),
            ],
        },
    }

    return render(request, "complaints/management_dashboard.html", {
        "complaints": complaints,
        "total": total,
        "resolved": status_counts.get("resolved", 0),
        "chart_data_json": json.dumps(chart_data),
    })


# ---------------------------------------------------------------------------
# PARENT
# ---------------------------------------------------------------------------
@role_required(User.Role.PARENT)
def parent_dashboard(request):
    children = User.objects.filter(parent=request.user)
    complaints = list(Complaint.objects.filter(student__in=children).select_related("student"))
    for c in complaints:
        c.label_for_display = c.label_for(request.user)
    return render(request, "complaints/parent_dashboard.html", {
        "complaints": complaints,
        "children": children,
    })


# ---------------------------------------------------------------------------
# NOTIFICATIONS
# ---------------------------------------------------------------------------
@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(recipient=request.user)
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, "complaints/notifications.html", {"notifications": notifications})


@login_required
def notification_open(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save(update_fields=["is_read"])
    return redirect("complaints:complaint_detail", pk=notif.complaint_id)
