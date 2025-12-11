import requests
from django.conf import settings


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

    res = call("core_user_create_users", params, method="POST")

    if isinstance(res, list) and len(res) > 0:
        return res[0]["id"]

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

    return call("enrol_manual_enrol_users", params, method="POST")


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

