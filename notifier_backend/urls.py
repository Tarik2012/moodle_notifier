from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Admin Django
    path("admin/", admin.site.urls),

    # HOME GENERAL (hub / shell)
    path("", include("hub.urls")),   # 👈 entrada al sistema

    # Moodle
    path("moodle/", include("core.urls")),

    # Salud laboral
    path("medical/", include("medical_alerts.urls", namespace="medical_alerts")),

    # Auth
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
]
