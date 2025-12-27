from datetime import timedelta
from django.utils import timezone

from medical_alerts.models import Employee, MedicalAlertLog


ALERT_15 = "15_days"


def get_employees_expiring_in_15_days():
    today = timezone.localdate()
    employees = Employee.objects.filter(is_active=True)

    result = []

    for emp in employees:
        expiry_date = emp.created_at.date() + timedelta(days=365)
        days_left = (expiry_date - today).days

        if days_left == 15:
            result.append((emp, expiry_date))

    return result


def already_alerted(company, employee, expiry_date):
    return MedicalAlertLog.objects.filter(
        company=company,
        employee=employee,
        alert_type=ALERT_15,
        expiry_date=expiry_date,
    ).exists()
