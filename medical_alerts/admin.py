from django.contrib import admin
from .models import Company, Employee, MedicalAlertLog


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email", "is_active", "created_at")
    search_fields = ("name", "cif", "contact_email")
    list_filter = ("is_active",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "company",
        "dni",
        "is_active",
        "created_at",
    )
    search_fields = ("first_name", "last_name", "dni", "company__name")
    list_filter = ("is_active", "company")
    autocomplete_fields = ("company",)


@admin.register(MedicalAlertLog)
class MedicalAlertLogAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "employee",
        "alert_type",
        "reference_date",
        "status",
        "sent_to",
        "created_at",
    )
    search_fields = (
        "company__name",
        "employee__first_name",
        "employee__last_name",
        "sent_to",
    )
    list_filter = ("alert_type", "status", "company")
    autocomplete_fields = ("company", "employee")
