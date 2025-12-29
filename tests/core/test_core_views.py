import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from core.models import Student, Course


def login(client):
    user = get_user_model().objects.create_user(
        username="user1",
        password="pass12345",
    )
    client.force_login(user)
    return user


@pytest.mark.django_db
def test_moodle_dashboard_view_template_and_counts(client):
    login(client)
    Student.objects.create(
        first_name="Ana",
        last_name="Lopez",
        email="ana.dashboard@example.com",
        phone_number="600000001",
    )
    Course.objects.create(
        moodle_course_id=201,
        name="Course A",
    )

    response = client.get(reverse("moodle_dashboard"))

    assert response.status_code == 200
    assertTemplateUsed(response, "moodle/home.html")
    assert response.context["student_count"] == 1
    assert response.context["course_count"] == 1


@pytest.mark.django_db
def test_student_list_view_requires_login(client):
    response = client.get(reverse("student_list"))

    assert response.status_code == 302
    assert response.url == f"/login/?next={reverse('student_list')}"


@pytest.mark.django_db
def test_student_list_view_template(client):
    login(client)
    Student.objects.create(
        first_name="Luis",
        last_name="Perez",
        email="luis.list@example.com",
        phone_number="600000002",
    )

    response = client.get(reverse("student_list"))

    assert response.status_code == 200
    assertTemplateUsed(response, "core/student_list.html")


@pytest.mark.django_db
def test_student_detail_view_template(client):
    login(client)
    student = Student.objects.create(
        first_name="Marta",
        last_name="Diaz",
        email="marta.detail@example.com",
        phone_number="600000003",
    )

    response = client.get(reverse("student_detail", args=[student.id]))

    assert response.status_code == 200
    assertTemplateUsed(response, "core/student_detail.html")
    assert response.context["student"] == student
