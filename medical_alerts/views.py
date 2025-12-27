from django.shortcuts import render, redirect
from .models import Employee
from .forms import EmployeeForm
from .forms import CompanyForm


def employee_create_view(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("medical_alerts:employee_create")
    else:
        form = EmployeeForm()

    return render(
        request,
        "medical_alerts/employee_create.html",
        {
            "form": form,
        },
    )




def company_create_view(request):
    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("medical_alerts:company_create")
    else:
        form = CompanyForm()

    return render(
        request,
        "medical_alerts/company_create.html",
        {
            "form": form,
        },
    )

