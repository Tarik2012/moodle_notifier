import requests
from django.conf import settings

from core.audit import log_external_sync


# ============================================================
# CONFIGURACIÓN MOODLE
# ============================================================

MOODLE_URL = settings.MOODLE_URL
TOKEN = settings.MOODLE_TOKEN

BASE_PARAMS = {
    "wstoken": TOKEN,
    "moodlewsrestformat": "json",
}


# ============================================================
# FUNCIÓN BASE PARA CONSULTAR LA API
# ============================================================

def call(function, extra_params=None, method="GET"):
    """
    Función genérica para llamar a cualquier endpoint Moodle.
    """
    params = BASE_PARAMS.copy()
    params["wsfunction"] = function

    if extra_params:
        params.update(extra_params)

    if method == "POST":
        res = requests.post(MOODLE_URL, params=params)
    else:
        res = requests.get(MOODLE_URL, params=params)

    try:
        return res.json()
    except:
        return {"error": "NO_JSON_RESPONSE", "raw": res.text}


# ============================================================
# 1) CREAR USUARIO
# ============================================================

def create_user(firstname, lastname, email, username, password, phone=None):
    """
    Crea un usuario en Moodle y devuelve el ID asignado.
    """
    params = {
        "users[0][firstname]": firstname,
        "users[0][lastname]": lastname,
        "users[0][email]": email,
        "users[0][username]": username,
        "users[0][password]": password,
    }

    if phone:
        params["users[0][phone1]"] = phone

    try:
        res = call("core_user_create_users", params, method="POST")

        if isinstance(res, list) and len(res) > 0:
            user_id = res[0]["id"]
            log_external_sync(
                service="moodle",
                action="create_user",
                entity_type="student",
                entity_id=user_id,
                status="success",
            )
            return user_id

        error_message = f"Error creando usuario: {res}"
        log_external_sync(
            service="moodle",
            action="create_user",
            entity_type="student",
            entity_id=None,
            status="error",
            message=error_message,
        )
    except Exception as exc:
        log_external_sync(
            service="moodle",
            action="create_user",
            entity_type="student",
            entity_id=None,
            status="error",
            message=str(exc),
        )
        raise

    raise Exception(f"Error creando usuario: {res}")


# ============================================================
# 2) OBTENER USUARIO POR ID
# ============================================================

def get_user_by_id(user_id):
    return call("core_user_get_users_by_field", {
        "field": "id",
        "values[0]": user_id
    })


# ============================================================
# 3) MATRICULAR USUARIO EN UN CURSO
# ============================================================

def enroll_user(user_id, course_id, role_id=5):
    """
    Matricula un usuario en un curso Moodle.
    role_id=5 es Estudiante.
    """
    params = {
        "enrolments[0][roleid]": role_id,
        "enrolments[0][userid]": user_id,
        "enrolments[0][courseid]": course_id,
    }

    try:
        res = call("enrol_manual_enrol_users", params, method="POST")
    except Exception as exc:
        log_external_sync(
            service="moodle",
            action="enroll_user",
            entity_type="enrollment",
            entity_id=user_id,
            status="error",
            message=str(exc),
        )
        raise

    if isinstance(res, dict) and res.get("exception"):
        log_external_sync(
            service="moodle",
            action="enroll_user",
            entity_type="enrollment",
            entity_id=user_id,
            status="error",
            message=f"{res}",
        )
    else:
        log_external_sync(
            service="moodle",
            action="enroll_user",
            entity_type="enrollment",
            entity_id=user_id,
            status="success",
            message=f"course_id={course_id}",
        )

    return res


# ============================================================
# 4) OBTENER CONTENIDO DE UN CURSO (para SCORM)
# ============================================================

def get_course_contents(course_id):
    return call("core_course_get_contents", {"courseid": course_id})


# ============================================================
# 5) OBTENER SCOES DE UN SCORM
# ============================================================

def get_scorm_scoes(scorm_id):
    return call("mod_scorm_get_scorm_scoes", {"scormid": scorm_id})


# ============================================================
# 6) OBTENER TRACKS (progreso de un SCO)
# ============================================================

def get_scorm_track(user_id, sco_id):
    return call("mod_scorm_get_scorm_sco_tracks", {
        "userid": user_id,
        "scoid": sco_id
    })


# ============================================================
# 7) CALCULAR PROGRESO DE UN SCORM
# ============================================================

def calculate_scorm_progress(scorm_id, user_id):
    scoes = get_scorm_scoes(scorm_id)
    sco_list = [
        s for s in scoes.get("scoes", [])
        if s.get("launch") and s.get("scormtype") == "sco"
    ]

    completed = 0
    total = len(sco_list)

    for sco in sco_list:
        track = get_scorm_track(user_id, sco["id"])
        status = "notattempted"

        for t in track.get("data", {}).get("tracks", []):
            if t["element"] in ["cmi.core.lesson_status", "status"]:
                status = t["value"]

        if status == "completed":
            completed += 1

    return (completed / total * 100) if total else 0


# ============================================================
# 8) CALCULAR PROGRESO GLOBAL DEL CURSO
# ============================================================

def calculate_course_progress(course_id, user_id):
    contents = get_course_contents(course_id)
    scorm_ids = []

    for c in contents:
        for m in c.get("modules", []):
            if m["modname"] == "scorm":
                scorm_ids.append(m["instance"])

    results = [
        calculate_scorm_progress(scorm_id, user_id)
        for scorm_id in scorm_ids
    ]

    return sum(results) / len(results) if results else 0


# ============================================================
# 9) ACTUALIZAR USUARIO
# ============================================================

def update_user(
    user_id,
    firstname=None,
    lastname=None,
    email=None,
    username=None,
    phone=None,
    city=None,
    address=None,
    company=None,
    dni=None,
):
    """
    Actualiza datos de usuario en Moodle.
    Nota: Moodle no actualiza city/address/company/dni por defecto; se guardan solo en la BD local.
    """
    params = {
        "users[0][id]": user_id,
    }

    if firstname is not None:
        params["users[0][firstname]"] = firstname
    if lastname is not None:
        params["users[0][lastname]"] = lastname
    if email is not None:
        params["users[0][email]"] = email
    # En este proyecto username = email; si cambia el email, actualizamos el username.
    username_to_use = username if username is not None else email
    if username_to_use is not None:
        params["users[0][username]"] = username_to_use
    if phone is not None:
        params["users[0][phone1]"] = phone

    try:
        res = call("core_user_update_users", params, method="POST")
    except Exception as exc:
        log_external_sync(
            service="moodle",
            action="update_user",
            entity_type="student",
            entity_id=user_id,
            status="error",
            message=str(exc),
        )
        raise

    if isinstance(res, dict) and res.get("exception"):
        error_message = f"Error actualizando usuario: {res}"
        log_external_sync(
            service="moodle",
            action="update_user",
            entity_type="student",
            entity_id=user_id,
            status="error",
            message=error_message,
        )
        raise Exception(error_message)

    log_external_sync(
        service="moodle",
        action="update_user",
        entity_type="student",
        entity_id=user_id,
        status="success",
    )

    return True


# ============================================================
# 10) BORRAR USUARIO
# ============================================================

def delete_user(user_id):
    """
    Borra un usuario en Moodle.
    """
    params = {"userids[0]": user_id}
    try:
        res = call("core_user_delete_users", params, method="POST")
    except Exception as exc:
        log_external_sync(
            service="moodle",
            action="delete_user",
            entity_type="student",
            entity_id=user_id,
            status="error",
            message=str(exc),
        )
        raise

    if isinstance(res, dict) and res.get("exception"):
        error_message = f"Error borrando usuario: {res}"
        log_external_sync(
            service="moodle",
            action="delete_user",
            entity_type="student",
            entity_id=user_id,
            status="error",
            message=error_message,
        )
        raise Exception(error_message)

    log_external_sync(
        service="moodle",
        action="delete_user",
        entity_type="student",
        entity_id=user_id,
        status="success",
    )

    return True
