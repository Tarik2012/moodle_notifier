from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .forms import EmployeeForm, CompanyForm
from .models import Company, Employee, MedicalAlertLog


# =====================================================
# DASHBOARD · SALUD LABORAL
# =====================================================
@login_required
def medical_dashboard_view(request):
    companies = Company.objects.filter(is_active=True)
    employees = Employee.objects.filter(is_active=True)

    company_count = companies.count()
    employee_count = employees.count()

    # Reconocimientos
    expiring_soon_count = sum(
        1 for e in employees if e.days_until_expiry() == 15
    )
    expired_count = sum(
        1 for e in employees if e.days_until_expiry() < 0
    )

    # Alertas por fecha
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)
    last_7_days_start = today - timedelta(days=6)  # incluye hoy

    alerts_today = MedicalAlertLog.objects.filter(
        created_at__date=today,
        status="sent",
    ).count()

    alerts_yesterday = MedicalAlertLog.objects.filter(
        created_at__date=yesterday,
        status="sent",
    ).count()

    alerts_last_7_days = MedicalAlertLog.objects.filter(
        created_at__date__gte=last_7_days_start,
        created_at__date__lte=today,
        status="sent",
    ).count()

    context = {
        "company_count": company_count,
        "employee_count": employee_count,
        "expiring_soon_count": expiring_soon_count,
        "expired_count": expired_count,
        "alerts_today": alerts_today,
        "alerts_yesterday": alerts_yesterday,
        "alerts_last_7_days": alerts_last_7_days,
    }

    return render(request, "medical/dashboard.html", context)


# =====================================================
# CREAR EMPLEADO
# =====================================================
@login_required
def employee_create_view(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(
                request,
                f"Empleado «{employee.first_name} {employee.last_name}» creado correctamente."
            )
            return redirect("medical_alerts:employee_create")
    else:
        form = EmployeeForm()

    return render(
        request,
        "medical_alerts/employee_create.html",
        {"form": form},
    )


# =====================================================
# CREAR EMPRESA
# =====================================================
@login_required
def company_create_view(request):
    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save()
            messages.success(
                request,
                f"Empresa «{company.name}» creada correctamente."
            )
            return redirect("medical_alerts:company_create")
    else:
        form = CompanyForm()

    return render(
        request,
        "medical_alerts/company_create.html",
        {"form": form},
    )
