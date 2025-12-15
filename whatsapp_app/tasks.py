from celery import shared_task
import os
from dotenv import load_dotenv
from whatsapp_app.services.whatsapp_client import send_test_template

load_dotenv()


@shared_task(queue="celery")
def send_test_whatsapp_task():
    return send_test_template(
        token=os.getenv("WHATSAPP_TOKEN"),
        phone_id=os.getenv("WHATSAPP_PHONE_ID"),
        to_number=os.getenv("WHATSAPP_TEST_TO"),
    )
