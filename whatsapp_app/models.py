from django.db import models
from core.models import Student, Course


class MessageLog(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    # RELACIONES (CLAVE)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="message_logs",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="message_logs",
        null=True,
        blank=True,
    )

    # METADATOS DEL MENSAJE
    phone_number = models.CharField(max_length=20)
    template_name = models.CharField(max_length=100)

    # Variables enviadas (auditoría)
    variables = models.JSONField()

    # ESTADO
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )

    # FECHAS
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["student", "course", "template_name"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return (
            f"{self.template_name} | "
            f"{self.student} | "
            f"{self.course or '-'} | "
            f"{self.status}"
        )
