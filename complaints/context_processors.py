from .models import Notification


def notifications(request):
    if not request.user.is_authenticated:
        return {}
    qs = Notification.objects.filter(recipient=request.user)
    return {
        "nav_notifications": qs[:8],
        "nav_unread_count": qs.filter(is_read=False).count(),
    }
