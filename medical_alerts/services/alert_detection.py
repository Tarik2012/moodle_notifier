from medical_alerts.models import Employee


def detect_alerts_today():
    alerts = {
        "30_days": [],
        "15_days": [],
        "expired": [],
    }

    employees = Employee.objects.filter(is_active=True)

    for emp in employees:
        days = emp.days_until_expiry()

        if days == 30:
            alerts["30_days"].append(emp)
        elif days == 15:
            alerts["15_days"].append(emp)
        elif days < 0:
            alerts["expired"].append(emp)

    return alerts
