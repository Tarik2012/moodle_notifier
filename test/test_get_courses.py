import requests
import yaml

# ===============================
# CONFIGURACIÓN
# ===============================

MOODLE_URL = "https://campus.formasuronline.es/webservice/rest/server.php"
TOKEN = "685bb904ebb611d8eb735c92c47e22d0"



def call(function, params=None):
    """Llama al API de Moodle."""
    p = {
        "wstoken": TOKEN,
        "wsfunction": function,
        "moodlewsrestformat": "json"
    }

    if params:
        p.update(params)

    response = requests.get(MOODLE_URL, params=p)
    return response.json()


# ===============================
# OBTENER CURSOS
# ===============================
print("⏳ Obteniendo lista de cursos desde Moodle...")

cursos = call("core_course_get_courses")

# Si hay error lo mostramos
if isinstance(cursos, dict) and "exception" in cursos:
    print("❌ ERROR:", cursos)
    exit()

print(f"📘 Cursos encontrados: {len(cursos)}")

# ===============================
# PROCESAR Y GUARDAR EN YAML
# ===============================
exportar = []

for c in cursos:
    exportar.append({
        "id": c["id"],
        "fullname": c["fullname"],
        "shortname": c.get("shortname", ""),
        "summary": c.get("summary", ""),
    })

with open("moodle_courses.yaml", "w", encoding="utf-8") as f:
    yaml.dump(exportar, f, allow_unicode=True, sort_keys=False)

print("✅ Archivo generado: moodle_courses.yaml")
