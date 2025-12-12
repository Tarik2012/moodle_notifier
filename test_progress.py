import requests
import json

MOODLE_URL = "https://campus.formasuronline.es/webservice/rest/server.php"
TOKEN = "685bb904ebb611d8eb735c92c47e22d0"

def call(wsfunction, params=None):
    base = {
        "wstoken": TOKEN,
        "wsfunction": wsfunction,
        "moodlewsrestformat": "json",
    }
    if params:
        base.update(params)

    r = requests.get(MOODLE_URL, params=base)
    return r.json()


# ======================================================
# 1. Obtener SCORMs del curso
# ======================================================
def get_scorms(course_id):
    return call("mod_scorm_get_scorms_by_courses", {
        "courseids[0]": course_id
    })


# ======================================================
# 2. Obtener tracking de un SCORM para un usuario
# ======================================================
def get_scorm_tracks(scorm_id, user_id):
    return call("mod_scorm_get_scorm_attempts", {
        "scormid": scorm_id,
        "userid": user_id
    })


def run_test():
    user_id = 6066              # tu alumno
    course_id = 24942           # probable SCORM; si falla obtenemos lista

    print("\n==============================")
    print("1) BUSCANDO SCORMS DEL CURSO…")
    print("==============================")

    scorms = get_scorms(course_id)
    print(json.dumps(scorms, indent=2))

    if "scorms" not in scorms or len(scorms["scorms"]) == 0:
        print("\nERROR: El curso no tiene SCORMs detectados.")
        return

    scorm_id = scorms["scorms"][0]["id"]
    print(f"\nPrimer SCORM encontrado: ID = {scorm_id}")

    print("\n==============================")
    print("2) BUSCANDO TRACKING DEL ALUMNO…")
    print("==============================")

    track = get_scorm_tracks(scorm_id, user_id)
    print(json.dumps(track, indent=2))

    print("\nFIN DE LA PRUEBA.")


if __name__ == "__main__":
    run_test()
