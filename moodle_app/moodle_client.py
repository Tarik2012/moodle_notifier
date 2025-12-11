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


# ====== FUNCIONES ESPECÍFICAS MOODLE ======

def get_user(user_id):
    return call("core_user_get_users_by_field", {
        "field": "id",
        "values[0]": user_id,
    })


def get_course(course_id):
    return call("core_course_get_courses", {
        "options[ids][0]": course_id,
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
