import pytest

from core.models import Student, Course, Enrollment


@pytest.mark.django_db
def test_student_course_enrollment_creation():
    student = Student.objects.create(
        first_name="Ana",
        last_name="Lopez",
        email="ana@example.com",
        phone_number="600000000",
    )
    course = Course.objects.create(
        moodle_course_id=101,
        name="Intro",
    )
    enrollment = Enrollment.objects.create(student=student, course=course)

    assert Student.objects.count() == 1
    assert Course.objects.count() == 1
    assert Enrollment.objects.count() == 1
    assert enrollment.student == student
    assert enrollment.course == course
