# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q

from .models import Student, Course, Enrollment
from .forms import StudentForm

# Moodle API
from moodle_app.api import (
    create_user,
    enroll_user,
    update_user,
    delete_user,
)


# ============================================================
# DASHBOARD
# ============================================================
def home_view(request):
    student_count = Student.objects.count()
    course_count = Course.objects.count()

    context = {
        "student_count": student_count,
        "course_count": course_count,
    }
    return render(request, "home.html", context)


# ============================================================
# LISTA DE ALUMNOS
# ============================================================
def student_list_view(request):
    estado = request.GET.get("estado")
    q = (request.GET.get("q") or "").strip()

    students = Student.objects.annotate(
        course_count=Count("enrollments", distinct=True)
    )

    if estado == "interno":
        students = students.filter(moodle_user_id__isnull=True)

    elif estado == "moodle":
        students = students.filter(moodle_user_id__isnull=False, course_count=0)

    elif estado == "matriculado":
        students = students.filter(course_count__gt=0)

    if q:
        students = students.filter(
            Q(email__icontains=q)
            | Q(dni__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
        )

    students = students.order_by("-created_at")

    paginator = Paginator(students, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "core/student_list.html",
        {
            "page_obj": page_obj,
            "students": page_obj.object_list,
            "estado": estado,
            "q": q,
        },
    )


# ============================================================
# CREAR ALUMNO (CREA TAMBIÉN USUARIO EN MOODLE)
# ============================================================
def create_student_view(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            password = form.cleaned_data.get("password")

            try:
                moodle_id = create_user(
                    firstname=student.first_name,
                    lastname=student.last_name,
                    email=student.email,
                    username=student.email,
                    password=password,
                    phone=student.phone_number,
                )
                student.moodle_user_id = moodle_id
                student.save()

                messages.success(request, "Alumno creado correctamente.")
                return redirect("student_list")

            except Exception as e:
                form.add_error(None, f"Error creando usuario en Moodle: {e}")
    else:
        form = StudentForm()

    return render(request, "core/create_student.html", {"form": form})


# ============================================================
# DETALLE DE ALUMNO
# ============================================================
def student_detail_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    enrollments = (
        Enrollment.objects
        .filter(student=student)
        .select_related("course")
    )

    return render(
        request,
        "core/student_detail.html",
        {
            "student": student,
            "enrollments": enrollments,
        },
    )


# ============================================================
# EDITAR ALUMNO (SINCRONIZA CON MOODLE)
# ============================================================
def student_edit_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    old_first_name = student.first_name
    old_last_name = student.last_name
    old_email = student.email
    old_phone = student.phone_number

    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save()

            if student.moodle_user_id:
                changed_fields = {}

                if old_first_name != student.first_name:
                    changed_fields["firstname"] = student.first_name
                if old_last_name != student.last_name:
                    changed_fields["lastname"] = student.last_name
                if old_email != student.email:
                    changed_fields["email"] = student.email
                    changed_fields["username"] = student.email
                if old_phone != student.phone_number:
                    changed_fields["phone"] = student.phone_number

                if changed_fields:
                    try:
                        update_user(
                            user_id=student.moodle_user_id,
                            **changed_fields,
                        )
                    except Exception as e:
                        messages.error(
                            request,
                            "Datos guardados en la BD, pero fallo al actualizar en Moodle. "
                            f"Pendiente de sincronizar: {e}",
                        )
                        return redirect("student_detail", student_id=student.id)

            messages.success(request, "Alumno actualizado correctamente.")
            return redirect("student_detail", student_id=student.id)
    else:
        form = StudentForm(instance=student)

    return render(
        request,
        "core/student_edit.html",
        {
            "student": student,
            "form": form,
        },
    )


# ============================================================
# ELIMINAR ALUMNO (BORRA TAMBIÉN EN MOODLE)
# ============================================================
def student_delete_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        if student.moodle_user_id:
            try:
                delete_user(student.moodle_user_id)
            except Exception as e:
                messages.error(
                    request,
                    "No se pudo borrar en Moodle. "
                    f"El alumno no se eliminó en la BD: {e}",
                )
                return redirect("student_detail", student_id=student.id)

        student.delete()
        messages.success(request, "Alumno eliminado correctamente.")
        return redirect("student_list")

    return render(
        request,
        "core/student_delete_confirm.html",
        {"student": student},
    )


# ============================================================
# CREAR USUARIO EN MOODLE (VISTA DEFENSIVA)
# ============================================================
def student_create_moodle_user_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if student.moodle_user_id:
        messages.warning(request, "Este alumno ya está creado en Moodle.")
    else:
        messages.error(
            request,
            "La creación del usuario en Moodle debe hacerse al crear el alumno "
            "con su contraseña.",
        )

    return redirect("student_detail", student_id=student.id)


# ============================================================
# ASIGNAR CURSO A UN ALUMNO
# ============================================================
from whatsapp_app.services.welcome import send_welcome_message


def student_assign_course_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    if not student.moodle_user_id:
        messages.error(request, "Este alumno aún no está creado en Moodle.")
        return redirect("student_detail", student_id=student.id)

    q = (request.GET.get("q") or "").strip()

    courses = Course.objects.all()

    if q:
        courses = courses.filter(
            Q(reference_code__icontains=q)
            | Q(name__icontains=q)
        )

    courses = courses.order_by("name")

    if request.method == "POST":
        course_id = request.POST.get("course_id")

        if not course_id:
            messages.error(request, "Selecciona un curso.")
            return redirect("student_assign_course", student_id=student.id)

        course = get_object_or_404(Course, id=course_id)

        # Evitar duplicados
        if Enrollment.objects.filter(student=student, course=course).exists():
            messages.warning(request, "Este alumno ya está asignado a este curso.")
            return redirect("student_detail", student_id=student.id)

        try:
            # 1️⃣ Matricular en Moodle
            enroll_user(
                user_id=student.moodle_user_id,
                course_id=course.moodle_course_id,
            )

            # 2️⃣ Guardar matrícula en la BD
            enrollment = Enrollment.objects.create(
                student=student,
                course=course,
            )

            # 4️⃣ Enviar mensaje de bienvenida
            send_welcome_message(
                student=student,
                enrollment=enrollment,
            )

            messages.success(
                request,
                f"Alumno asignado al curso «{course.name}» correctamente.",
            )
            return redirect("student_detail", student_id=student.id)

        except Exception as e:
            messages.error(request, f"Error matriculando en Moodle: {e}")

    return render(
        request,
        "core/student_assign_course.html",
        {
            "student": student,
            "courses": courses,
            "q": q,
        },
    )
