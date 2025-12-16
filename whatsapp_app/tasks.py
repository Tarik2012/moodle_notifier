from celery import shared_task
import os
from whatsapp_app.services.whatsapp_client import send_template_message
from whatsapp_app.models import MessageLog


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 10})
def send_whatsapp_template_task(
    self,
    *,
    to_number: str,
    template_name: str,
    language: str = "en_US",
    variables: list[str] | None = None,
):
    log = MessageLog.objects.create(
        phone_number=to_number,
        template_name=template_name,
        status=MessageLog.Status.PENDING,
    )

    try:
        status, response = send_template_message(
            token=os.getenv("WHATSAPP_TOKEN"),
            phone_id=os.getenv("WHATSAPP_PHONE_ID"),
            to_number=to_number,
            template_name=template_name,
            language=language,
            variables=variables,
        )

        log.status = MessageLog.Status.SENT if status == 200 else MessageLog.Status.FAILED
        log.save(update_fields=["status"])

        return status, response

    except Exception:
        log.status = MessageLog.Status.FAILED
        log.save(update_fields=["status"])
        raise
