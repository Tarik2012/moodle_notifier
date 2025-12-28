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

    expiring_soon_count = sum(
        1 for e in employees if e.days_until_expiry() == 15
    )

    expired_count = sum(
        1 for e in employees if e.days_until_expiry() < 0
    )

    recent_alerts = (
        MedicalAlertLog.objects
        .select_related("employee")
        .order_by("-created_at")[:5]
    )

    context = {
        "company_count": company_count,
        "employee_count": employee_count,
        "expiring_soon_count": expiring_soon_count,
        "expired_count": expired_count,
        "recent_alerts": recent_alerts,
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
