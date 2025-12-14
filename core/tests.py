from django.test import Client, TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch

from core.models import Student


TEST_DB_SETTINGS = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}


@override_settings(DATABASES=TEST_DB_SETTINGS)
class StudentIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("core.views.create_user", return_value=None)
    def test_create_student_without_moodle_user_id(self, mock_create_user):
        response = self.client.post(
            reverse("student_create"),
            data={
                "first_name": "Ana",
                "last_name": "Local",
                "email": "ana.local@example.com",
                "phone_number": "600000001",
                "password": "password123",
            },
        )

        self.assertEqual(response.status_code, 302)
        student = Student.objects.get(email="ana.local@example.com")
        self.assertIsNone(student.moodle_user_id)
        mock_create_user.assert_called_once()

    @patch("core.views.create_user", return_value=9876)
    def test_create_student_with_moodle_user_id(self, mock_create_user):
        response = self.client.post(
            reverse("student_create"),
            data={
                "first_name": "Bea",
                "last_name": "Moodle",
                "email": "bea.moodle@example.com",
                "phone_number": "600000002",
                "password": "password123",
            },
        )

        self.assertEqual(response.status_code, 302)
        student = Student.objects.get(email="bea.moodle@example.com")
        self.assertEqual(student.moodle_user_id, 9876)
        mock_create_user.assert_called_once()

    def test_edit_local_student_persists_changes(self):
        student = Student.objects.create(
            first_name="Carlos",
            last_name="Original",
            email="carlos@example.com",
            phone_number="600000003",
            moodle_user_id=None,
        )

        response = self.client.post(
            reverse("student_edit", args=[student.id]),
            data={
                "first_name": "Carlos",
                "last_name": "Actualizado",
                "email": "carlos.updated@example.com",
                "phone_number": "600000009",
            },
        )

        self.assertEqual(response.status_code, 302)
        student.refresh_from_db()
        self.assertEqual(student.last_name, "Actualizado")
        self.assertEqual(student.email, "carlos.updated@example.com")
        self.assertEqual(student.phone_number, "600000009")

    def test_delete_student_without_moodle_user_id(self):
        student = Student.objects.create(
            first_name="Diana",
            last_name="Temporal",
            email="diana@example.com",
            phone_number="600000004",
            moodle_user_id=None,
        )

        response = self.client.post(
            reverse("student_delete", args=[student.id]),
            data={},
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Student.objects.filter(id=student.id).exists())
