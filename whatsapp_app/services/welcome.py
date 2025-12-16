from __future__ import annotations

from django.db import transaction

from whatsapp_app.tasks import send_whatsapp_template_task
from whatsapp_app.models import MessageLog


WELCOME_TEMPLATE = "jaspers_market_plain_text_v1"
WELCOME_LANG = "en_US"


def send_welcome_message(*, student, enrollment) -> None:
    """
    Regla de dominio: enviar mensaje de bienvenida al alumno (si procede).
    - No hace llamadas externas directas.
    - Encola la tarea Celery.
    - Evita duplicados básicos por plantilla + teléfono.
    """

    # 1) Validación mínima
    phone = getattr(student, "phone_number", None) or getattr(student, "phone", None)
    if not phone:
        return

    # 2) Idempotencia básica (evitar re-envío accidental)
    already_sent = MessageLog.objects.filter(
        phone_number=phone,
        template_name=WELCOME_TEMPLATE,
        status="SENT",
    ).exists()
    if already_sent:
        return

    # 3) Encolar task (SIN variables porque la plantilla no las acepta)
    transaction.on_commit(
        lambda: send_whatsapp_template_task.delay(
            to_number=phone,
            template_name=WELCOME_TEMPLATE,
            language=WELCOME_LANG,
            variables=None,   # 👈 CLAVE
        )
    )
