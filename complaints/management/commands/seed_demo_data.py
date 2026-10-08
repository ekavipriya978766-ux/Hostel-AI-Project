from django.core.management.base import BaseCommand

from accounts.models import User
from complaints.models import Complaint


DEMO_PASSWORD = "HostelAI@123"


class Command(BaseCommand):
    help = "Creates one demo account per role (+ sample complaints) so you can log in immediately."

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(
            username="admin_demo", defaults=dict(role=User.Role.ADMIN, first_name="Site", last_name="Admin", email="admin@hostelai.local"),
        )
        admin.set_password(DEMO_PASSWORD)
        admin.role = User.Role.ADMIN
        admin.save()

        management, _ = User.objects.get_or_create(
            username="management_demo",
            defaults=dict(role=User.Role.MANAGEMENT, first_name="Priya", last_name="Menon", email="management@hostelai.local"),
        )
        management.set_password(DEMO_PASSWORD)
        management.save()

        warden_electrical, _ = User.objects.get_or_create(
            username="warden_electrical",
            defaults=dict(role=User.Role.WARDEN, department="Electrical", first_name="Ravi", last_name="Kumar", email="warden.electrical@hostelai.local"),
        )
        warden_electrical.set_password(DEMO_PASSWORD)
        warden_electrical.role = User.Role.WARDEN
        warden_electrical.department = "Electrical"
        warden_electrical.save()

        warden_general, _ = User.objects.get_or_create(
            username="warden_general",
            defaults=dict(role=User.Role.WARDEN, department="General", first_name="Anita", last_name="Rao", email="warden.general@hostelai.local"),
        )
        warden_general.set_password(DEMO_PASSWORD)
        warden_general.role = User.Role.WARDEN
        warden_general.department = "General"
        warden_general.save()

        parent, _ = User.objects.get_or_create(
            username="parent_demo",
            defaults=dict(role=User.Role.PARENT, first_name="Suresh", last_name="Iyer", email="parent@hostelai.local"),
        )
        parent.set_password(DEMO_PASSWORD)
        parent.save()

        student, _ = User.objects.get_or_create(
            username="student_demo",
            defaults=dict(role=User.Role.STUDENT, room_number="A-204", parent=parent, first_name="Arjun", last_name="Iyer", email="student@hostelai.local"),
        )
        student.set_password(DEMO_PASSWORD)
        student.role = User.Role.STUDENT
        student.room_number = "A-204"
        student.parent = parent
        student.save()

        sample_complaints = [
            ("Sparking socket in my room", "There is a short circuit in the wall socket near my study table, it sparked when I plugged in my charger."),
            ("No hot water since two days", "The geyser in my bathroom stopped working two days ago, only cold water is coming."),
            ("Requesting an extra blanket", "It's getting cold at night, could I please get an extra blanket for my room."),
        ]
        for title, description in sample_complaints:
            if not Complaint.objects.filter(student=student, title=title).exists():
                Complaint.objects.create(student=student, title=title, description=description)

        self.stdout.write(self.style.SUCCESS("Demo data ready. Password for every demo account: " + DEMO_PASSWORD))
        self.stdout.write("  admin_demo / management_demo / warden_electrical / warden_general / parent_demo / student_demo")
