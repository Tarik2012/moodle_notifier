from unittest import mock

import pytest

from core.models import Course, Student
from whatsapp_app.models import MessageLog
from whatsapp_app.tasks import send_whatsapp_template_task


@pytest.mark.django_db
def test_send_whatsapp_template_task_creates_log_and_marks_sent(monkeypatch):
    monkeypatch.setenv("WHATSAPP_TOKEN", "token")
    monkeypatch.setenv("WHATSAPP_PHONE_ID", "phone_id")

    mock_send = mock.Mock(return_value=(200, "ok"))
    monkeypatch.setattr("whatsapp_app.tasks.send_template_message", mock_send)

    student = Student.objects.create(
        first_name="Ana",
        last_name="Lopez",
        email="ana@example.com",
        phone_number="34600000000",
    )
    course = Course.objects.create(
        moodle_course_id=101,
        name="Course 1",
    )

    result = send_whatsapp_template_task(
        to_number=student.phone_number,
        template_name="progress_student_service_v1",
        language="es",
        variables=["Ana"],
        student_id=student.id,
        course_id=course.id,
    )

    log = MessageLog.objects.get(
        student=student,
        course=course,
        template_name="progress_student_service_v1",
    )

    assert log.status == MessageLog.Status.SENT
    assert log.variables == ["Ana"]
    mock_send.assert_called_once()
    assert result["status_code"] == 200