from __future__ import annotations

from datetime import timedelta
from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from core.models import Enrollment
from whatsapp_app.models import MessageLog
from whatsapp_app.tasks import send_whatsapp_template_task


# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================

LANG_ES = "es"
PROGRESS_DEDUPLICATION_DAYS = 2

PROGRESS_TEMPLATE = "progress_student_service_v1"
REVIEW_TEMPLATE = "review_student_service_v1"
COMPLETION_TEMPLATE = "completion_student_service_v1"


# =====================================================
# REGLA 2 – PROGRESO
# =====================================================

@shared_task
def dispatch_progress_messages() -> None:
    now = timezone.now()
    dedup_from = now - timedelta(days=PROGRESS_DEDUPLICATION_DAYS)

    enrollment_ids = (
        Enrollment.objects
        .filter(progress__gt=0, progress__lt=100)
        .exclude(
            Q(student__phone_number__isnull=True) |
            Q(student__phone_number="")
        )
        .values_list("id", flat=True)
    )

    for enrollment_id in enrollment_ids:
        send_progress_message_for_enrollment.delay(
            enrollment_id=enrollment_id,
            dedup_from_iso=dedup_from.isoformat(),
        )


@shared_task(bind=True)
def send_progress_message_for_enrollment(
    self,
    *,
    enrollment_id: int,
    dedup_from_iso: str,
) -> None:
    dedup_from = timezone.datetime.fromisoformat(dedup_from_iso)

    try:
        enr = (
            Enrollment.objects
            .select_related("student", "course")
            .get(id=enrollment_id)
        )
    except Enrollment.DoesNotExist:
        return

    student = enr.student
    course = enr.course
    progress = round(enr.progress, 2)

    already_sent = MessageLog.objects.filter(
        student=student,
        course=course,
        template_name=PROGRESS_TEMPLATE,
        created_at__gte=dedup_from,
        status__in=[
            MessageLog.Status.PENDING,
            MessageLog.Status.SENT,
        ],
    ).exists()

    if already_sent:
        return

    send_whatsapp_template_task.delay(
        to_number=student.phone_number,
        template_name=PROGRESS_TEMPLATE,
        language=LANG_ES,
        variables=[
            student.first_name,
            course.name,
            str(progress),
        ],
        student_id=student.id,
        course_id=course.id,
    )


# =====================================================
# REGLA 3 – REPASO (DÍA ANTES)
# =====================================================

@shared_task
def dispatch_review_messages() -> None:
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)

    enrollment_ids = (
        Enrollment.objects
        .filter(
            progress__gte=100,
            course__end_date=tomorrow,
            course__end_date__isnull=False,
        )
        .exclude(
            Q(student__phone_number__isnull=True) |
            Q(student__phone_number="")
        )
        .values_list("id", flat=True)
    )

    for enrollment_id in enrollment_ids:
        send_review_message_for_enrollment.delay(enrollment_id=enrollment_id)


@shared_task(bind=True)
def send_review_message_for_enrollment(
    self,
    *,
    enrollment_id: int,
) -> None:
    try:
        enr = (
            Enrollment.objects
            .select_related("student", "course")
            .get(id=enrollment_id)
        )
    except Enrollment.DoesNotExist:
        return

    student = enr.student
    course = enr.course

    already_sent = MessageLog.objects.filter(
        student=student,
        course=course,
        template_name=REVIEW_TEMPLATE,
        status__in=[
            MessageLog.Status.PENDING,
            MessageLog.Status.SENT,
        ],
    ).exists()

    if already_sent:
        return

    send_whatsapp_template_task.delay(
        to_number=student.phone_number,
        template_name=REVIEW_TEMPLATE,
        language=LANG_ES,
        variables=[
            student.first_name,
            course.name,
        ],
        student_id=student.id,
        course_id=course.id,
    )


# =====================================================
# REGLA 4 – FINALIZACIÓN
# =====================================================

@shared_task
def dispatch_completion_messages() -> None:
    today = timezone.now().date()

    enrollment_ids = (
        Enrollment.objects
        .filter(
            progress__gte=100,
            course__end_date=today,
            course__end_date__isnull=False,
        )
        .exclude(
            Q(student__phone_number__isnull=True) |
            Q(student__phone_number="")
        )
        .values_list("id", flat=True)
    )

    for enrollment_id in enrollment_ids:
        send_completion_message_for_enrollment.delay(enrollment_id=enrollment_id)


@shared_task(bind=True)
def send_completion_message_for_enrollment(
    self,
    *,
    enrollment_id: int,
) -> None:
    try:
        enr = (
            Enrollment.objects
            .select_related("student", "course")
            .get(id=enrollment_id)
        )
    except Enrollment.DoesNotExist:
        return

    student = enr.student
    course = enr.course
    progress = round(enr.progress, 2)

    already_sent = MessageLog.objects.filter(
        student=student,
        course=course,
        template_name=COMPLETION_TEMPLATE,
        status__in=[
            MessageLog.Status.PENDING,
            MessageLog.Status.SENT,
        ],
    ).exists()

    if already_sent:
        return

    send_whatsapp_template_task.delay(
        to_number=student.phone_number,
        template_name=COMPLETION_TEMPLATE,
        language=LANG_ES,
        variables=[
            student.first_name,
            course.name,
            str(progress),
        ],
        student_id=student.id,
        course_id=course.id,
    )


# core/tasks.py
from celery import shared_task
from django.core.management import call_command


@shared_task(bind=True)
def sync_courses_task(self):
    call_command("sync_courses")

