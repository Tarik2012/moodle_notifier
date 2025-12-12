import requests
import os

MOODLE_URL = os.getenv("MOODLE_URL")
MOODLE_TOKEN = os.getenv("MOODLE_TOKEN")

BASE_PARAMS = {
    "wstoken": MOODLE_TOKEN,
    "moodlewsrestformat": "json",
}


def call(function_name, extra_params=None):
    """
    Llamada general a Moodle Web Services.
    """
    params = BASE_PARAMS.copy()
    params["wsfunction"] = function_name

    if extra_params:
        params.update(extra_params)

    response = requests.get(MOODLE_URL, params=params, timeout=20)

    try:
        return response.json()
    except:
        return {"error": "Invalid JSON response from Moodle"}


# ======================================================
#                FUNCIONES ESPECÍFICAS MOODLE
# ======================================================

def get_user(user_id):
    return call("core_user_get_users_by_field", {
        "field": "id",
        "values[0]": user_id,
    })


def get_course(course_id):
    return call("core_course_get_courses", {
        "options[ids][0]": course_id,
    })


def get_course_contents(course_id):
    """
    Devuelve todas las secciones y módulos del curso.
    (Necesario para detectar SCORMs).
    """
    return call("core_course_get_contents", {
        "courseid": course_id
    })


def get_scorm_scoes(scorm_id):
    return call("mod_scorm_get_scorm_scoes", {
        "scormid": scorm_id
    })


def get_scorm_tracks(scorm_id, user_id):
    return call("mod_scorm_get_scorm_sco_tracks", {
        "scormid": scorm_id,
        "userid": user_id
    })


# ======================================================
#                PROGRESO REAL DEL CURSO
# ======================================================

def get_course_progress(user_id, course_id):
    """
    Devuelve el progreso REAL del curso (SCORMs) como porcentaje.
    """

    # 1) Obtener contenidos
    contents = get_course_contents(course_id)

    if isinstance(contents, dict) and "exception" in contents:
        return 0

    scorm_ids = []

    # Buscar SCORMs dentro del curso
    for section in contents:
        for mod in section.get("modules", []):
            if mod.get("modname") == "scorm":
                scorm_ids.append(mod.get("instance"))

    if not scorm_ids:
        return 0

    total_progress = 0
    scorm_count = 0

    # 2) Procesar cada SCORM
    for scormid in scorm_ids:

        scoes = get_scorm_scoes(scormid)

        sco_list = [
            s for s in scoes.get("scoes", [])
            if s.get("launch") and s.get("scormtype") == "sco"
        ]

        total_scoes = len(sco_list)
        completados = 0

        for sco in sco_list:
            track = call("mod_scorm_get_scorm_sco_tracks", {
                "userid": user_id,
                "scoid": sco["id"]
            })

            status = "notattempted"

            for t in track.get("data", {}).get("tracks", []):
                if t["element"] in ["cmi.core.lesson_status", "status"]:
                    status = t["value"]

            if status == "completed":
                completados += 1

        progreso_scorm = (completados / total_scoes) * 100 if total_scoes > 0 else 0

        total_progress += progreso_scorm
        scorm_count += 1

    # Media de progreso de todos los SCORMs del curso
    return round(total_progress / scorm_count, 2) if scorm_count > 0 else 0
