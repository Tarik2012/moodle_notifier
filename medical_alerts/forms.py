from django import forms
from .models import Company, Employee


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "cif", "contact_email", "is_active"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "cif": forms.TextInput(attrs={"class": "form-input"}),
            "contact_email": forms.EmailInput(attrs={"class": "form-input"}),
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ["company", "first_name", "last_name", "dni", "is_active"]

        widgets = {
            "company": forms.Select(attrs={"class": "form-select"}),
            "first_name": forms.TextInput(attrs={"class": "form-input"}),
            "last_name": forms.TextInput(attrs={"class": "form-input"}),
            "dni": forms.TextInput(attrs={"class": "form-input"}),
        }
