"""
Implements the automated workflow from the spec:

  Student submits complaint
    -> AI predicts severity (and, hidden internally, the department)
    -> Complaint stored in DB
    -> Alert/notification triggered to management + the matching warden
       + the linked parent (never to the submitting student)
    -> Management dashboard updates automatically (just a fresh query)
    -> Warden later handles the issue and updates status (see
       complaints.views.update_status, which logs the change and notifies
       the student + parent + management).
"""

from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from accounts.models import User
from .models import Complaint, Notification, StatusUpdate
from .ml.severity_predictor import predict_severity
from .utils import detect_department


@receiver(pre_save, sender=Complaint)
def process_new_complaint(sender, instance: Complaint, **kwargs):
    """Runs the AI severity + hidden department detection exactly once,
    right before the very first save, and snapshots the student's room."""
    if instance.pk:
        return  # already exists - this is an update (e.g. status change), skip AI step

    if not instance.room_number:
        instance.room_number = instance.student.room_number

    combined_text = f"{instance.title}. {instance.description}"

    severity, confidence = predict_severity(combined_text)
    instance.severity = severity
    instance.severity_confidence = confidence

    department = detect_department(combined_text)
    instance.department = department

    warden = (
        User.objects.filter(role=User.Role.WARDEN, department=department, is_active=True).first()
        or User.objects.filter(role=User.Role.WARDEN, department="General", is_active=True).first()
    )
    instance.assigned_warden = warden


@receiver(post_save, sender=Complaint)
def alert_on_new_complaint(sender, instance: Complaint, created, **kwargs):
    if not created:
        return

    StatusUpdate.objects.create(
        complaint=instance,
        old_status="",
        new_status=instance.status,
        changed_by=instance.student,
        note="Complaint submitted by student.",
    )

    recipients = set(
        User.objects.filter(role=User.Role.MANAGEMENT, is_active=True)
    )
    if instance.assigned_warden:
        recipients.add(instance.assigned_warden)
    if instance.student.parent_id:
        recipients.add(instance.student.parent)

    message = (
        f"New complaint from {instance.student.get_full_name() or instance.student.username} "
        f"(Room {instance.room_number}) - severity: {instance.get_severity_display()}."
    )
    Notification.objects.bulk_create([
        Notification(
            recipient=recipient,
            complaint=instance,
            notif_type=Notification.NotifType.NEW_COMPLAINT,
            message=message,
        )
        for recipient in recipients
    ])
