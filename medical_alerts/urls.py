from django.urls import path
from . import views

app_name = "medical_alerts"

urlpatterns = [
    path("employees/create/", views.employee_create_view, name="employee_create"),
    path("companies/create/", views.company_create_view, name="company_create"),
    
]
