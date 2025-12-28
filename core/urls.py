# urls.py
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from core import views as core_views


urlpatterns = [




    # ============================
    # MOODLE
    # ============================
    path("moodle/", core_views.moodle_dashboard_view, name="moodle_dashboard"),
    path("courses/sync/", core_views.sync_courses_view, name="sync_courses"),

    # ============================
    # AUTH
    # ============================
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # ============================
    # ALUMNOS
    # ============================
    path("students/", core_views.student_list_view, name="student_list"),
    path("students/create/", core_views.create_student_view, name="student_create"),
    path("students/<int:student_id>/", core_views.student_detail_view, name="student_detail"),
    path("students/<int:student_id>/edit/", core_views.student_edit_view, name="student_edit"),
    path("students/<int:student_id>/delete/", core_views.student_delete_view, name="student_delete"),
    path(
        "students/<int:student_id>/create-moodle-user/",
        core_views.student_create_moodle_user_view,
        name="student_create_moodle_user",
    ),
    path(
        "students/<int:student_id>/assign/",
        core_views.student_assign_course_view,
        name="student_assign_course",
    ),

    # ============================
    # ADMIN
    # ============================
    path("admin/", admin.site.urls),
]
