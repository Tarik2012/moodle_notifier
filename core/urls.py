from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from core import views as core_views


urlpatterns = [

    # ============================
    # HOME
    # ============================
    path("", core_views.home_view, name="home"),

    # ============================
    # AUTH
    # ============================
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # ============================
    # ALUMNOS (CRUD)
    # ============================
    path("students/", core_views.student_list_view, name="student_list"),
    path("students/create/", core_views.create_student_view, name="student_create"),

    # Detalles
    path("students/<int:student_id>/", core_views.student_detail_view, name="student_detail"),
    path("students/<int:student_id>/edit/", core_views.student_edit_view, name="student_edit"),
    path("students/<int:student_id>/delete/", core_views.student_delete_view, name="student_delete"),

    # Crear usuario en Moodle
    path(
        "students/<int:student_id>/create-moodle-user/",
        core_views.student_create_moodle_user_view,
        name="student_create_moodle_user"
    ),

    # Asignación de curso (placeholder)
    path(
        "students/<int:student_id>/assign/",
        core_views.student_assign_course_view,
        name="student_assign_course"
    ),

    # ============================
    # ADMIN
    # ============================
    path("admin/", admin.site.urls),
]
