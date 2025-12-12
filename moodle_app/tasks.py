from celery import shared_task
from core.models import Enrollment
from moodle_app.services.moodle_progress import calculate_course_progress


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 30})
def update_all_enrollments_progress(self):
    enrollments = (
        Enrollment.objects
        .select_related("student", "course")
        .filter(student__moodle_user_id__isnull=False)
    )

    for enr in enrollments:
        progress = calculate_course_progress(
            moodle_user_id=enr.student.moodle_user_id,
            moodle_course_id=enr.course.moodle_course_id
        )

        enr.progress = round(progress, 2)
        enr.save(update_fields=["progress"])
