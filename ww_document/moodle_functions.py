"""
===========================================================
 MOODLE API - FUNCIONES DE REFERENCIA (APUNTES OFICIALES)
 Proyecto: Moodle WhatsApp Notifier
===========================================================

Este archivo contiene TODAS las funciones Moodle
que hemos usado o vamos a usar, organizadas por categorías:

1. Función base call()
2. Crear usuario
3. Obtener usuario
4. Matricular usuario en un curso
5. Obtener contenido del curso (SCORMs)
6. Obtener SCOEs (los elementos de un SCORM)
7. Obtener tracks (progreso real del alumno)
8. Funciones avanzadas de progreso
9. Notas importantes y errores frecuentes
"""

import requests

# ===========================================
# CONFIGURACIÓN
# ===========================================
MOODLE_URL = "https://campus.formasuronline.es/webservice/rest/server.php"
TOKEN = "PON_AQUI_TU_TOKEN_REAL"

BASE_PARAMS = {
    "wstoken": TOKEN,
    "moodlewsrestformat": "json",
}


# ===========================================
# 1) FUNCIÓN GENERAL DE LLAMADA A MOODLE
# ===========================================
def call(funcion, extra_params=None, method="GET"):
    """
    Llama a cualquier endpoint de Moodle.

    funcion: nombre de la función Moodle, ej. 'core_user_create_users'
    extra_params: diccionario con parámetros
    method: GET o POST (depende de Moodle)

    return: JSON con la respuesta
    """
    params = BASE_PARAMS.copy()
    params["wsfunction"] = funcion

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


# =====================================================
# 2) CREAR USUARIO NUEVO
# =====================================================
def create_user(firstname, lastname, email, username, password, phone=None):
    """
    Crea un usuario nuevo en Moodle y DEVUELVE el ID del usuario.

    Ejemplo uso:
        user_id = create_user("Tarik", "Derouiche", "correo@test.com",
                              "tarik_demo", "Pass1234!", "612345678")

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
        return res[0]["id"]  # ← EL ID IMPORTANTE

    raise Exception(f"Error creando usuario: {res}")


# =====================================================
# 3) OBTENER USUARIO POR ID
# =====================================================
def get_user_by_id(user_id):
    return call("core_user_get_users_by_field", {
        "field": "id",
        "values[0]": user_id
    })


# =====================================================
# 4) MATRICULAR USUARIO EN UN CURSO
# =====================================================
def enroll_user(user_id, course_id, role_id=5):
    """
    role_id = 5 → Estudiante (por defecto)
    """

    params = {
        "enrolments[0][roleid]": role_id,
        "enrolments[0][userid]": user_id,
        "enrolments[0][courseid]": course_id,
    }

    res = call("enrol_manual_enrol_users", params, method="POST")
    return res  # normalmente devuelve {}


# =====================================================
# 5) OBTENER CONTENIDO DEL CURSO (para detectar SCORMs)
# =====================================================
def get_course_contents(course_id):
    return call("core_course_get_contents", {
        "courseid": course_id
    })


# =====================================================
# 6) OBTENER SCOEs DE UN SCORM
# =====================================================
def get_scorm_scoes(scorm_id):
    return call("mod_scorm_get_scorm_scoes", {
        "scormid": scorm_id
    })


# =====================================================
# 7) OBTENER TRACKS (PROGRESO REAL DE UN SCO)
# =====================================================
def get_scorm_track(user_id, sco_id):
    """
    Track = el progreso REAL del alumno en un SCO del SCORM.
    """
    return call("mod_scorm_get_scorm_sco_tracks", {
        "userid": user_id,
        "scoid": sco_id
    })


# =====================================================
# 8) FUNCIONES AVANZADAS DE PROGRESO (RESUMEN)
# =====================================================
def calculate_scorm_progress(scorm_id, user_id):
    """
    Calcula el % de progreso real de UN SCORM.
    """
    scoes = get_scorm_scoes(scorm_id)
    sco_list = [s for s in scoes.get("scoes", [])
                if s.get("launch") and s.get("scormtype") == "sco"]

    completados = 0
    total = len(sco_list)

    for sco in sco_list:
        track = get_scorm_track(user_id, sco["id"])
        status = "notattempted"

        for t in track.get("data", {}).get("tracks", []):
            if t["element"] in ["cmi.core.lesson_status", "status"]:
                status = t["value"]

        if status == "completed":
            completados += 1

    progreso = (completados / total * 100) if total > 0 else 0

    return progreso


def calculate_course_progress(course_id, user_id):
    """
    Suma el progreso de TODOS los SCORM del curso.
    """
    data = get_course_contents(course_id)
    scorms = []

    for s in data:
        for m in s.get("modules", []):
            if m["modname"] == "scorm":
                scorms.append(m["instance"])

    resultados = []

    for scorm_id in scorms:
        p = calculate_scorm_progress(scorm_id, user_id)
        resultados.append(p)

    if resultados:
        return sum(resultados) / len(resultados)

    return 0


# =====================================================
# 9) NOTAS IMPORTANTES
# =====================================================

"""
✔ core_user_create_users → SÍ devuelve el ID del usuario creado.
✔ enrol_manual_enrol_users → normalmente devuelve {} si fue bien.
✔ mod_scorm_get_scorm_scoes → obtiene los SCOEs (elementos del SCORM)
✔ mod_scorm_get_scorm_sco_tracks → obtiene el progreso REAL del alumno.
✔ core_course_get_contents → permite detectar TODOS los SCORM del curso.

ERRORES FRECUENTES:

❌ "No permission to view module" → El rol del token Moodle no tiene permisos.
❌ "Invalid parameter value detected" → El parámetro está mal escrito.
❌ Respuesta HTML → Se ha usado GET en vez de POST (o viceversa).
❌ 'exception' in respuesta → El token no tiene permiso para la función.

Este archivo es SOLO DE REFERENCIA.
No es parte del proyecto Django, es un manual del programador.
"""
