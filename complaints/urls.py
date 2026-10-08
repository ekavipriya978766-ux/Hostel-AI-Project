from django.urls import path

from . import views

app_name = "complaints"

urlpatterns = [
    path("student/", views.student_dashboard, name="student_dashboard"),
    path("warden/", views.warden_dashboard, name="warden_dashboard"),
    path("management/", views.management_dashboard, name="management_dashboard"),
    path("parent/", views.parent_dashboard, name="parent_dashboard"),
    path("complaint/<int:pk>/", views.complaint_detail, name="complaint_detail"),
    path("notifications/", views.notifications_list, name="notifications_list"),
    path("notifications/<int:pk>/open/", views.notification_open, name="notification_open"),
]
