from celery import shared_task

from medical_alerts.services.send_alerts import send_15_day_alerts


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 60})
def send_medical_alerts_15_days(self):
    """
    Celery task to send medical expiry alerts (15 days).
    La lógica está en services, aquí solo se dispara la tarea.
    """
    send_15_day_alerts()
