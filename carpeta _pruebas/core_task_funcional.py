from __future__ import annotations

from celery import shared_task
from django.db.models import Q

from core.models import Enrollment
from whatsapp_app.tasks import send_whatsapp_template_task


# Plantilla REAL que ya sabes que funciona
PROGRESS_TEMPLATE = "welcome_student_service_v1"

# Idioma EXACTO de la plantilla en Meta
PROGRESS_LANG = "en"


@shared_task(bind=True)
def send_progress_messages(self) -> None:
    """
    TASK DE PRUEBA CONTROLADA
    - SIN throttle
    - SIN deduplicación
    - Solo para verificar envío
    """

    enrollments = (
        Enrollment.objects
        .select_related("student")
        .filter(progress__gt=0, progress__lt=100)
        .exclude(
            Q(student__phone_number__isnull=True) |
            Q(student__phone_number="")
        )
    )

    for enr in enrollments:
        send_whatsapp_template_task.delay(
            to_number=enr.student.phone_number,
            template_name=PROGRESS_TEMPLATE,
            language=PROGRESS_LANG,
            variables=[
                enr.student.first_name,  # {{1}}
            ],
        )
