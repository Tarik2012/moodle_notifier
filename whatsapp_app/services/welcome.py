from __future__ import annotations

from django.db import transaction

from whatsapp_app.tasks import send_whatsapp_template_task
from whatsapp_app.models import MessageLog


WELCOME_TEMPLATE = "welcome_student_service_v1"
WELCOME_LANG = "es"


def send_welcome_message(*, student, enrollment) -> None:
    """
    Regla de dominio: enviar mensaje de bienvenida al alumno (si procede).

    - Se ejecuta al crear la matrícula
    - No hace llamadas externas directas
    - Usa Celery
    - Evita duplicados básicos
    """

    # --------------------------------------------------
    # 1) Validación mínima
    # --------------------------------------------------
    phone = getattr(student, "phone_number", None) or getattr(student, "phone", None)
    if not phone:
        return

    course = enrollment.course

    # --------------------------------------------------
    # 2) Idempotencia básica (welcome = 1 vez por curso)
    # --------------------------------------------------
    already_sent = MessageLog.objects.filter(
        phone_number=phone,
        template_name=WELCOME_TEMPLATE,
        student_id=student.id,
        course_id=course.id,
        status=MessageLog.Status.SENT,
    ).exists()

    if already_sent:
        return

    # --------------------------------------------------
    # 3) Preparar variables (PROTEGIENDO fechas)
    # --------------------------------------------------
    start_date = (
        course.start_date.strftime("%d/%m/%Y")
        if course.start_date
        else ""
    )

    end_date = (
        course.end_date.strftime("%d/%m/%Y")
        if course.end_date
        else ""
    )

    variables = [
        student.first_name,  # {{1}}
        course.name,         # {{2}}
        start_date,          # {{3}}
        end_date,            # {{4}}
    ]

    # --------------------------------------------------
    # 4) Encolar task SOLO tras commit
    # --------------------------------------------------
    transaction.on_commit(
        lambda: send_whatsapp_template_task.delay(
            to_number=phone,
            template_name=WELCOME_TEMPLATE,
            language=WELCOME_LANG,
            variables=variables,
            student_id=student.id,
            course_id=course.id,
        )
    )
