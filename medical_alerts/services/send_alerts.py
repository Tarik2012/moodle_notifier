from django.conf import settings
from django.core.mail import send_mail

from medical_alerts.models import MedicalAlertLog
from medical_alerts.services.alert_detection import detect_alerts_today


ALERT_15 = "15_days"


def already_sent(company, employee, alert_type, reference_date):
    return MedicalAlertLog.objects.filter(
        company=company,
        employee=employee,
        alert_type=alert_type,
        reference_date=reference_date,
        status="sent",
    ).exists()


def send_15_day_alerts():
    alerts = detect_alerts_today()
    employees_15 = alerts["15_days"]

    companies = {}
    for emp in employees_15:
        companies.setdefault(emp.company, []).append(emp)

    for company, employees in companies.items():
        # Filtrar empleados a los que NO se les haya enviado ya
        employees_to_send = []
        for emp in employees:
            if not already_sent(
                company=company,
                employee=emp,
                alert_type=ALERT_15,
                reference_date=emp.medical_expiry_date,
            ):
                employees_to_send.append(emp)

        if not employees_to_send:
            continue

        subject = "Aviso: reconocimiento médico próximo a caducar (15 días)"

        lines = [
            "Los siguientes empleados deben renovar su reconocimiento médico en 15 días:",
            "",
        ]
        for emp in employees_to_send:
            lines.append(f"- {emp.first_name} {emp.last_name}")

        message = "\n".join(lines)

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [company.contact_email],
            fail_silently=False,
        )

        for emp in employees_to_send:
            MedicalAlertLog.objects.create(
                company=company,
                employee=emp,
                alert_type=ALERT_15,
                reference_date=emp.medical_expiry_date,
                status="sent",
                sent_to=company.contact_email,
            )
