from django.core.management.base import BaseCommand

from complaints.ml.train_severity_model import train_and_save


class Command(BaseCommand):
    help = "Train (or retrain) the offline AI severity-prediction model."

    def handle(self, *args, **options):
        train_and_save()
        self.stdout.write(self.style.SUCCESS("Severity model trained successfully."))
