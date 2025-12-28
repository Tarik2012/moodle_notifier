from django.core.management.base import BaseCommand
from medical_alerts.tasks import send_medical_alerts_15_days

class Command(BaseCommand):
    help = "Dispatch 15-day medical alerts via Celery"

    def handle(self, *args, **options):
        send_medical_alerts_15_days.delay()
        self.stdout.write(self.style.SUCCESS("Medical alerts task dispatched"))
