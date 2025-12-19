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


# =====================================================
# REGLA 2 – MENSAJES DE SEGUIMIENTO
# =====================================================

PROGRESS_TEMPLATE = "progress_student_service_v1"


@shared_task(bind=True)
def send_progress_messages(self) -> None:
    """
    REGLA 2 – MENSAJES DE SEGUIMIENTO

    - Progreso entre 1% y 99%
    - Alumno con teléfono
    - Dedupe: alumno + curso + plantilla
    - Ventana: 2 días
    """

    now = timezone.now()
    dedup_from = now - timedelta(days=PROGRESS_DEDUPLICATION_DAYS)

    enrollments = (
        Enrollment.objects
        .select_related("student", "course")
        .filter(progress__gt=0, progress__lt=100)
        .exclude(
            Q(student__phone_number__isnull=True) |
            Q(student__phone_number="")
        )
    )

    for enr in enrollments:
        student = enr.student
        course = enr.course
        progress = round(enr.progress, 2)

        already_sent = MessageLog.objects.filter(
            student=student,
            course=course,
            template_name=PROGRESS_TEMPLATE,
            created_at__gte=dedup_from,
            status=MessageLog.Status.SENT,
        ).exists()

        if already_sent:
            continue

        send_whatsapp_template_task.delay(
            to_number=student.phone_number,
            template_name=PROGRESS_TEMPLATE,
            language=LANG_ES,
            variables=[
                student.first_name,   # {{1}}
                course.name,          # {{2}}
                str(progress),        # {{3}}
            ],
            student_id=student.id,
            course_id=course.id,
        )


# # =====================================================
# # REGLA 3 – MODO REPASO (DÍA ANTES DE FINALIZAR)
# # =====================================================

# REVIEW_TEMPLATE = "review_student_service_v1"


# @shared_task(bind=True)
# def send_review_messages(self) -> None:
#     """
#     REGLA 3 – MODO REPASO

#     - Curso finaliza mañana
#     - Progreso = 100%
#     - Alumno con teléfono
#     - Un solo mensaje
#     """

#     today = timezone.now().date()
#     tomorrow = today + timedelta(days=1)

#     enrollments = (
#         Enrollment.objects
#         .select_related("student", "course")
#         .filter(progress=100, course__end_date=tomorrow)
#         .exclude(
#             Q(student__phone_number__isnull=True) |
#             Q(student__phone_number="")
#         )
#     )

#     for enr in enrollments:
#         student = enr.student
#         course = enr.course

#         already_sent = MessageLog.objects.filter(
#             student=student,
#             course=course,
#             template_name=REVIEW_TEMPLATE,
#             status=MessageLog.Status.SENT,
#         ).exists()

#         if already_sent:
#             continue

#         send_whatsapp_template_task.delay(
#             to_number=student.phone_number,
#             template_name=REVIEW_TEMPLATE,
#             language=LANG_ES,
#             variables=[
#                 student.first_name,  # {{1}}
#                 course.name,         # {{2}}
#             ],
#             student_id=student.id,
#             course_id=course.id,
#         )


# # =====================================================
# # REGLA 4 – FINALIZACIÓN DE CURSO
# # =====================================================

# COMPLETION_TEMPLATE = "completion_student_service_v1"


# @shared_task(bind=True)
# def send_completion_messages(self) -> None:
#     """
#     REGLA 4 – FINALIZACIÓN DE CURSO

#     - Curso finaliza hoy
#     - Progreso = 100%
#     - Alumno con teléfono
#     - Un solo mensaje
#     """

#     today = timezone.now().date()

#     enrollments = (
#         Enrollment.objects
#         .select_related("student", "course")
#         .filter(progress=100, course__end_date=today)
#         .exclude(
#             Q(student__phone_number__isnull=True) |
#             Q(student__phone_number="")
#         )
#     )

#     for enr in enrollments:
#         student = enr.student
#         course = enr.course
#         progress = round(enr.progress, 2)

#         already_sent = MessageLog.objects.filter(
#             student=student,
#             course=course,
#             template_name=COMPLETION_TEMPLATE,
#             status=MessageLog.Status.SENT,
#         ).exists()

#         if already_sent:
#             continue

#         send_whatsapp_template_task.delay(
#             to_number=student.phone_number,
#             template_name=COMPLETION_TEMPLATE,
#             language=LANG_ES,
#             variables=[
#                 student.first_name,  # {{1}}
#                 course.name,         # {{2}}
#                 str(progress),       # {{3}} → siempre 100
#             ],
#             student_id=student.id,
#             course_id=course.id,
#         )
