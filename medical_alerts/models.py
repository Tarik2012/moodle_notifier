from __future__ import annotations

from datetime import timedelta

from django.db import models
from django.utils import timezone


# =====================================================
# COMPANY
# =====================================================
class Company(models.Model):
    name = models.CharField(max_length=255)
    cif = models.CharField(max_length=32, blank=True, default="")
    contact_email = models.EmailField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


# =====================================================
# EMPLOYEE
# =====================================================
class Employee(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="employees"
    )

    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=180, blank=True, default="")
    dni = models.CharField(max_length=32, blank=True, default="")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["company__name", "last_name", "first_name"]
        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["dni"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        full = f"{self.first_name} {self.last_name}".strip()
        return f"{full} ({self.company.name})"

    # =========================
    # MEDICAL LOGIC
    # =========================

    @property
    def medical_expiry_date(self):
        """
        Fecha en la que caduca el reconocimiento médico.
        Regla v1: 1 año (365 días) desde la fecha de alta del empleado.
        """
        return self.created_at.date() + timedelta(days=365)

    def days_until_expiry(self) -> int:
        """
        Días restantes hasta la caducidad del reconocimiento médico.
        Puede ser negativo si ya está caducado.
        """
        today = timezone.localdate()
        return (self.medical_expiry_date - today).days


# =====================================================
# MEDICAL ALERT LOG
# =====================================================
class MedicalAlertLog(models.Model):
    ALERT_30 = "30_days"
    ALERT_15 = "15_days"
    ALERT_EXPIRED = "expired"

    ALERT_TYPE_CHOICES = [
        (ALERT_30, "30 days before"),
        (ALERT_15, "15 days before"),
        (ALERT_EXPIRED, "Expired"),
    ]

    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="medical_alert_logs"
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="medical_alert_logs"
    )

    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)

    # Fecha de referencia del ciclo médico (expiry_date)
    reference_date = models.DateField()

    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    error_message = models.TextField(blank=True, default="")

    sent_to = models.EmailField()
    provider_message_id = models.CharField(max_length=255, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "employee", "alert_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return (
            f"{self.company.name} | "
            f"{self.employee_id} | "
            f"{self.alert_type} | "
            f"{self.status}"
        )
