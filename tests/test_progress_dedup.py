from datetime import timedelta
from unittest import mock

import pytest
from django.utils import timezone

from core.models import Course, Enrollment, Student
from core.tasks import PROGRESS_TEMPLATE, send_progress_message_for_enrollment
from whatsapp_app.models import MessageLog


@pytest.mark.django_db
def test_progress_dedup_skips_send_when_log_exists(monkeypatch):
    student = Student.objects.create(
        first_name="Ana",
        last_name="Lopez",
        email="ana2@example.com",
        phone_number="34600000001",
    )
    course = Course.objects.create(
        moodle_course_id=102,
        name="Course 2",
    )
    enrollment = Enrollment.objects.create(
        student=student,
        course=course,
        progress=50,
    )

    MessageLog.objects.create(
        student=student,
        course=course,
        phone_number=student.phone_number,
        template_name=PROGRESS_TEMPLATE,
        variables=[],
        status=MessageLog.Status.SENT,
    )

    mock_task = mock.Mock()
    mock_task.delay = mock.Mock()
    monkeypatch.setattr("core.tasks.send_whatsapp_template_task", mock_task)

    dedup_from = (timezone.now() - timedelta(days=1)).isoformat()
    send_progress_message_for_enrollment(
        enrollment_id=enrollment.id,
        dedup_from_iso=dedup_from,
    )

    mock_task.delay.assert_not_called()
    assert MessageLog.objects.filter(template_name=PROGRESS_TEMPLATE).count() == 1