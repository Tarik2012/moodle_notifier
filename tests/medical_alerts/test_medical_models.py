import pytest

from medical_alerts.models import Company, Employee, MedicalAlertLog


@pytest.mark.django_db
def test_company_employee_medical_alert_log_creation():
    company = Company.objects.create(
        name="Acme",
        cif="A1",
        contact_email="hr@acme.test",
        is_active=True,
    )
    employee = Employee.objects.create(
        company=company,
        first_name="Ana",
        last_name="Perez",
        dni="123",
        is_active=True,
    )
    log = MedicalAlertLog.objects.create(
        company=company,
        employee=employee,
        alert_type=MedicalAlertLog.ALERT_15,
        reference_date=employee.medical_expiry_date,
        status=MedicalAlertLog.STATUS_SENT,
        sent_to=company.contact_email,
    )

    assert MedicalAlertLog.objects.count() == 1
    assert log.company == company
    assert log.employee == employee
