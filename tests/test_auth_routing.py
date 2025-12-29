import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import Student
from medical_alerts.models import Company


@pytest.mark.django_db
def test_unauthenticated_access_redirects_to_login(client):
    student = Student.objects.create(
        first_name="Ana",
        last_name="Lopez",
        email="ana.auth@example.com",
        phone_number="600000010",
    )
    Company.objects.create(
        name="Auth Co",
        cif="AUTH",
        contact_email="auth@example.com",
        is_active=True,
    )

    urls = [
        reverse("hub_home"),
        reverse("moodle_dashboard"),
        reverse("student_list"),
        reverse("student_detail", args=[student.id]),
        reverse("medical_alerts:medical_dashboard"),
        reverse("medical_alerts:employee_create"),
        reverse("medical_alerts:company_create"),
    ]

    for url in urls:
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == f"/login/?next={url}"


@pytest.mark.django_db
def test_authenticated_access_returns_ok(client):
    user = get_user_model().objects.create_user(
        username="user1",
        password="pass12345",
    )
    client.force_login(user)
    student = Student.objects.create(
        first_name="Ben",
        last_name="Auth",
        email="ben.auth@example.com",
        phone_number="600000011",
    )
    Company.objects.create(
        name="Auth Co",
        cif="AUTH",
        contact_email="auth@example.com",
        is_active=True,
    )

    urls = [
        reverse("hub_home"),
        reverse("moodle_dashboard"),
        reverse("student_list"),
        reverse("student_detail", args=[student.id]),
        reverse("medical_alerts:medical_dashboard"),
        reverse("medical_alerts:employee_create"),
        reverse("medical_alerts:company_create"),
    ]

    for url in urls:
        response = client.get(url)
        assert response.status_code == 200
