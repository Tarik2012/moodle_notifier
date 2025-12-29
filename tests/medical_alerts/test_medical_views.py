import pytest

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertTemplateUsed

from medical_alerts.models import Company, Employee, MedicalAlertLog


def login(client):
    user = get_user_model().objects.create_user(
        username="user1",
        password="pass12345",
    )
    client.force_login(user)
    return user


@pytest.mark.django_db
def test_medical_dashboard_context_counts(client):
    login(client)
    active_company = Company.objects.create(
        name="Active Co",
        cif="C1",
        contact_email="active@example.com",
        is_active=True,
    )
    inactive_company = Company.objects.create(
        name="Inactive Co",
        cif="C2",
        contact_email="inactive@example.com",
        is_active=False,
    )

    now = timezone.now()

    emp_15 = Employee.objects.create(
        company=active_company,
        first_name="Eva",
        last_name="Soon",
        dni="1",
        is_active=True,
    )
    Employee.objects.filter(id=emp_15.id).update(created_at=now - timedelta(days=350))
    emp_15.refresh_from_db()

    emp_expired = Employee.objects.create(
        company=active_company,
        first_name="Max",
        last_name="Expired",
        dni="2",
        is_active=True,
    )
    Employee.objects.filter(id=emp_expired.id).update(created_at=now - timedelta(days=370))
    emp_expired.refresh_from_db()

    emp_other = Employee.objects.create(
        company=active_company,
        first_name="Ola",
        last_name="Other",
        dni="3",
        is_active=True,
    )
    Employee.objects.filter(id=emp_other.id).update(created_at=now - timedelta(days=100))
    emp_other.refresh_from_db()

    Employee.objects.create(
        company=inactive_company,
        first_name="Ina",
        last_name="Inactive",
        dni="4",
        is_active=False,
    )

    log_today = MedicalAlertLog.objects.create(
        company=active_company,
        employee=emp_15,
        alert_type=MedicalAlertLog.ALERT_15,
        reference_date=emp_15.medical_expiry_date,
        status=MedicalAlertLog.STATUS_SENT,
        sent_to=active_company.contact_email,
    )
    MedicalAlertLog.objects.filter(id=log_today.id).update(created_at=now)

    log_yesterday = MedicalAlertLog.objects.create(
        company=active_company,
        employee=emp_expired,
        alert_type=MedicalAlertLog.ALERT_EXPIRED,
        reference_date=emp_expired.medical_expiry_date,
        status=MedicalAlertLog.STATUS_SENT,
        sent_to=active_company.contact_email,
    )
    MedicalAlertLog.objects.filter(id=log_yesterday.id).update(created_at=now - timedelta(days=1))

    log_last_7 = MedicalAlertLog.objects.create(
        company=active_company,
        employee=emp_other,
        alert_type=MedicalAlertLog.ALERT_30,
        reference_date=emp_other.medical_expiry_date,
        status=MedicalAlertLog.STATUS_SENT,
        sent_to=active_company.contact_email,
    )
    MedicalAlertLog.objects.filter(id=log_last_7.id).update(created_at=now - timedelta(days=6))

    log_failed = MedicalAlertLog.objects.create(
        company=active_company,
        employee=emp_other,
        alert_type=MedicalAlertLog.ALERT_15,
        reference_date=emp_other.medical_expiry_date + timedelta(days=1),
        status=MedicalAlertLog.STATUS_FAILED,
        sent_to=active_company.contact_email,
    )
    MedicalAlertLog.objects.filter(id=log_failed.id).update(created_at=now)

    log_old = MedicalAlertLog.objects.create(
        company=active_company,
        employee=emp_other,
        alert_type=MedicalAlertLog.ALERT_EXPIRED,
        reference_date=emp_other.medical_expiry_date + timedelta(days=2),
        status=MedicalAlertLog.STATUS_SENT,
        sent_to=active_company.contact_email,
    )
    MedicalAlertLog.objects.filter(id=log_old.id).update(created_at=now - timedelta(days=10))

    response = client.get(reverse("medical_alerts:medical_dashboard"))

    assert response.status_code == 200
    assertTemplateUsed(response, "medical/dashboard.html")

    context = response.context
    assert context["company_count"] == 1
    assert context["employee_count"] == 3
    assert context["expiring_soon_count"] == 1
    assert context["expired_count"] == 1
    assert context["alerts_today"] == 1
    assert context["alerts_yesterday"] == 1
    assert context["alerts_last_7_days"] == 3


@pytest.mark.django_db
def test_employee_create_view_post_creates(client):
    login(client)
    company = Company.objects.create(
        name="Build Co",
        cif="B1",
        contact_email="hr@build.example",
        is_active=True,
    )

    response = client.post(
        reverse("medical_alerts:employee_create"),
        data={
            "company": company.id,
            "first_name": "Luis",
            "last_name": "Herrera",
            "dni": "DNI1",
            "is_active": True,
        },
    )

    assert response.status_code == 302
    assert Employee.objects.filter(company=company, first_name="Luis").exists()


@pytest.mark.django_db
def test_company_create_view_post_creates(client):
    login(client)

    response = client.post(
        reverse("medical_alerts:company_create"),
        data={
            "name": "New Co",
            "cif": "NC1",
            "contact_email": "contact@newco.test",
            "is_active": True,
        },
    )

    assert response.status_code == 302
    assert Company.objects.filter(name="New Co").exists()
