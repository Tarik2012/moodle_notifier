from __future__ import annotations

from django.db import transaction

from whatsapp_app.tasks import send_whatsapp_template_task
from whatsapp_app.models import MessageLog


WELCOME_TEMPLATE = "welcome_student_service_v1"
WELCOME_LANG = "es"


def send_welcome_message(*, student, enrollment) -> None:
    """
    Regla de dominio: enviar mensaje de bienvenida al alumno (si procede).
    - No hace llamadas externas directas.
    - Encola la tarea Celery.
    - Evita duplicados básicos por plantilla + teléfono.
    """

    # 1️⃣ Validación mínima
    phone = getattr(student, "phone_number", None) or getattr(student, "phone", None)
    if not phone:
        return

    # 2️⃣ Idempotencia básica
    already_sent = MessageLog.objects.filter(
        phone_number=phone,
        template_name=WELCOME_TEMPLATE,
        status=MessageLog.Status.SENT,
    ).exists()
    if already_sent:
        return

    course = enrollment.course

    # 3️⃣ Encolar task CON variables
    transaction.on_commit(
        lambda: send_whatsapp_template_task.delay(
            to_number=phone,
            template_name=WELCOME_TEMPLATE,
            language=WELCOME_LANG,
            variables=[
                student.first_name,                             # {{1}}
                course.name,                                    # {{2}}
                course.start_date.strftime("%d/%m/%Y"),         # {{3}}
                course.end_date.strftime("%d/%m/%Y"),           # {{4}}
            ],
            student_id=student.id,
            course_id=course.id,
        )
    )
