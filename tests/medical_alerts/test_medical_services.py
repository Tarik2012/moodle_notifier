import pytest

from datetime import timedelta

from django.utils import timezone

from medical_alerts.models import Company, Employee, MedicalAlertLog
from medical_alerts.services import send_alerts


@pytest.mark.django_db
def test_send_15_day_alerts_creates_log_and_avoids_duplicates(monkeypatch):
    company = Company.objects.create(
        name="Alert Co",
        cif="AC1",
        contact_email="alerts@example.com",
        is_active=True,
    )
    employee = Employee.objects.create(
        company=company,
        first_name="Nora",
        last_name="Soon",
        dni="N1",
        is_active=True,
    )
    Employee.objects.filter(id=employee.id).update(created_at=timezone.now() - timedelta(days=350))
    employee.refresh_from_db()

    def fake_detect():
        return {"30_days": [], "15_days": [employee], "expired": []}

    sent = {"count": 0}

    def fake_send_mail(subject, message, from_email, recipient_list, fail_silently):
        sent["count"] += 1
        sent["recipient_list"] = recipient_list

    monkeypatch.setattr(send_alerts, "detect_alerts_today", fake_detect)
    monkeypatch.setattr(send_alerts, "send_mail", fake_send_mail)

    send_alerts.send_15_day_alerts()

    assert sent["count"] == 1
    assert sent["recipient_list"] == [company.contact_email]

    logs = MedicalAlertLog.objects.filter(
        company=company,
        employee=employee,
        alert_type=send_alerts.ALERT_15,
        status=MedicalAlertLog.STATUS_SENT,
    )
    assert logs.count() == 1
    assert logs.first().sent_to == company.contact_email

    send_alerts.send_15_day_alerts()
    assert MedicalAlertLog.objects.filter(
        company=company,
        employee=employee,
        alert_type=send_alerts.ALERT_15,
        status=MedicalAlertLog.STATUS_SENT,
    ).count() == 1
