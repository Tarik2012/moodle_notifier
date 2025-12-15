from celery import shared_task
import os
from dotenv import load_dotenv
from whatsapp_app.services.whatsapp_client import send_test_template
from whatsapp_app.models import MessageLog

load_dotenv()


@shared_task(queue="celery")
def send_test_whatsapp_task():
    phone_number = os.getenv("WHATSAPP_TEST_TO")
    template_name = "jaspers_market_plain_text_v1"

    log = MessageLog.objects.create(
        phone_number=phone_number or "",
        template_name=template_name,
        status=MessageLog.Status.PENDING,
    )

    try:
        status_code, response_text = send_test_template(
            token=os.getenv("WHATSAPP_TOKEN"),
            phone_id=os.getenv("WHATSAPP_PHONE_ID"),
            to_number=phone_number,
        )

        log.status = MessageLog.Status.SENT if status_code == 200 else MessageLog.Status.FAILED
        log.save(update_fields=["status"])
        return status_code, response_text

    except Exception:
        log.status = MessageLog.Status.FAILED
        log.save(update_fields=["status"])
        raise
