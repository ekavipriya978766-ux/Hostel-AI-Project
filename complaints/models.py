from django.conf import settings
from django.db import models
from django.urls import reverse


def complaint_image_path(instance, filename):
    return f"complaint_images/{instance.student_id}/{filename}"


class Complaint(models.Model):
    class Severity(models.TextChoices):
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"

    class Status(models.TextChoices):
        NEW = "new", "New"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="complaints_filed",
        limit_choices_to={"role": "student"},
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    image = models.ImageField(upload_to=complaint_image_path, blank=True, null=True)

    # Snapshot of the room at submission time (in case the student moves later).
    room_number = models.CharField(max_length=10, blank=True)

    # --- AI-generated fields -------------------------------------------------
    # Internal department is intentionally NEVER shown on the student-facing
    # UI - it's only used behind the scenes for routing to the right warden.
    department = models.CharField(max_length=30, blank=True)
    severity = models.CharField(max_length=10, choices=Severity.choices, blank=True)
    severity_confidence = models.FloatField(default=0.0)

    status = models.CharField(max_length=15, choices=Status.choices, default=Status.NEW)
    assigned_warden = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_complaints",
        limit_choices_to={"role": "warden"},
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} {self.title} ({self.get_severity_display() or 'unscored'})"

    def get_absolute_url(self):
        return reverse("complaints:complaint_detail", args=[self.pk])

    @property
    def severity_badge_class(self):
        return {
            self.Severity.HIGH: "bg-danger",
            self.Severity.MEDIUM: "bg-warning text-dark",
            self.Severity.LOW: "bg-success",
        }.get(self.severity, "bg-secondary")

    @property
    def status_badge_class(self):
        return {
            self.Status.NEW: "bg-secondary",
            self.Status.IN_PROGRESS: "bg-info text-dark",
            self.Status.RESOLVED: "bg-success",
        }.get(self.status, "bg-secondary")

    def label_for(self, user):
        """
        Implements: a complaint shows as "My Complaint" to the student who
        filed it, and as "New Complaint" to every staff-side viewer (warden /
        management) who has not opened it yet, otherwise just "Complaint".
        """
        if user.id == self.student_id:
            return "My Complaint"
        if not ComplaintView.objects.filter(complaint=self, user=user).exists():
            return "New Complaint"
        return "Complaint"

    def mark_viewed_by(self, user):
        ComplaintView.objects.get_or_create(complaint=self, user=user)


class ComplaintView(models.Model):
    """Tracks which staff/parent users have opened a given complaint, so we
    can tell 'New Complaint' apart from an already-reviewed one."""

    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="views")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("complaint", "user")


class StatusUpdate(models.Model):
    """Full audit trail of status changes, used for complaint history."""

    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="status_updates")
    old_status = models.CharField(max_length=15, blank=True, choices=Complaint.Status.choices)
    new_status = models.CharField(max_length=15, choices=Complaint.Status.choices)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Complaint #{self.complaint_id}: {self.old_status or '—'} -> {self.new_status}"


class Notification(models.Model):
    """
    Internal alert sent to everyone relevant EXCEPT the complaining student
    (management, the assigned warden, and the linked parent), plus status
    updates sent back to the student/parent once a warden acts.
    """

    class NotifType(models.TextChoices):
        NEW_COMPLAINT = "new_complaint", "New Complaint"
        STATUS_UPDATE = "status_update", "Status Update"

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="notifications")
    notif_type = models.CharField(max_length=20, choices=NotifType.choices)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"To {self.recipient}: {self.message}"
