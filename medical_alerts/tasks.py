from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

from medical_alerts.models import MedicalAlertLog
from medical_alerts.services.medical_alerts import (
    get_employees_expiring_in_15_days,
    already_alerted,
    ALERT_15,
)


@shared_task
def send_medical_alerts_15_days():
    alerts = get_employees_expiring_in_15_days()

    companies = {}

    for employee, expiry_date in alerts:
        if already_alerted(employee.company, employee, expiry_date):
            continue

        companies.setdefault(employee.company, []).append(employee)

    for company, employees in companies.items():
        subject = "Aviso: reconocimiento médico próximo a caducar"

        body_lines = [
            "Los siguientes empleados deben renovar su reconocimiento médico en 15 días:",
            "",
        ]

        for emp in employees:
            body_lines.append(f"- {emp.first_name} {emp.last_name}")

        message = "\n".join(body_lines)

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [company.contact_email],
            fail_silently=False,
        )

        for emp in employees:
            MedicalAlertLog.objects.create(
                company=company,
                employee=emp,
                alert_type=ALERT_15,
                expiry_date=expiry_date,
                status="sent",
                sent_to=company.contact_email,
            )
