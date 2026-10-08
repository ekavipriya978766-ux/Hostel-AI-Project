from django.contrib import admin

from .models import Complaint, ComplaintView, Notification, StatusUpdate


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "student", "room_number", "department", "severity", "status", "assigned_warden", "created_at")
    list_filter = ("severity", "status", "department")
    search_fields = ("title", "description", "student__username", "room_number")
    readonly_fields = ("severity", "severity_confidence", "department", "created_at", "updated_at")


@admin.register(StatusUpdate)
class StatusUpdateAdmin(admin.ModelAdmin):
    list_display = ("complaint", "old_status", "new_status", "changed_by", "created_at")
    list_filter = ("new_status",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "complaint", "notif_type", "is_read", "created_at")
    list_filter = ("notif_type", "is_read")


@admin.register(ComplaintView)
class ComplaintViewAdmin(admin.ModelAdmin):
    list_display = ("complaint", "user", "viewed_at")
