from celery import shared_task
import os

from whatsapp_app.services.whatsapp_client import send_template_message
from whatsapp_app.models import MessageLog


@shared_task(bind=True)
def send_whatsapp_template_task(
    self,
    *,
    to_number: str,
    template_name: str,
    language: str = "en_US",
    variables: list[str] | None = None,

    # ⬇️ NUEVOS CAMPOS (OPCIONALES)
    student_id: int | None = None,
    course_id: int | None = None,
):
    """
    Envío de mensajes WhatsApp por plantilla.

    Reglas IMPORTANTES:
    - Un intento = un MessageLog
    - NO autoretry
    - Estado claro: PENDING -> SENT | FAILED
    """

    # 1️⃣ Crear log del intento (MISMA LÓGICA)
    log = MessageLog.objects.create(
        phone_number=to_number,
        template_name=template_name,
        status=MessageLog.Status.PENDING,

        # ⬇️ NUEVO (NO OBLIGATORIO)
        student_id=student_id,
        course_id=course_id,
        variables=variables or [],
    )

    try:
        token = os.getenv("WHATSAPP_TOKEN")
        phone_id = os.getenv("WHATSAPP_PHONE_ID")

        if not token or not phone_id:
            log.status = MessageLog.Status.FAILED
            log.save(update_fields=["status"])
            return {
                "error": "Missing WHATSAPP_TOKEN or WHATSAPP_PHONE_ID",
            }

        status_code, response = send_template_message(
            token=token,
            phone_id=phone_id,
            to_number=to_number,
            template_name=template_name,
            language=language,
            variables=variables,
        )

        log.status = (
            MessageLog.Status.SENT
            if status_code == 200
            else MessageLog.Status.FAILED
        )
        log.save(update_fields=["status"])

        return {
            "status_code": status_code,
            "response": response,
        }

    except Exception as exc:
        log.status = MessageLog.Status.FAILED
        log.save(update_fields=["status"])

        return {
            "error": str(exc),
        }
