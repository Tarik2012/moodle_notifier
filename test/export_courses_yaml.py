import requests
import yaml
import re


MOODLE_URL = "https://campus.formasuronline.es/webservice/rest/server.php"
TOKEN = "685bb904ebb611d8eb735c92c47e22d0"

def call(func, params=None):
    base = {
        "wstoken": TOKEN,
        "wsfunction": func,
        "moodlewsrestformat": "json"
    }
    if params:
        base.update(params)
    return requests.get(MOODLE_URL, params=base).json()


def extract_reference(text):
    """ Extrae referencia tipo 159/03 o 06802/01 """
    if not text:
        return None
    match = re.search(r"\b\d{2,5}/\d{1,2}\b", text)
    return match.group(0) if match else None


print("⏳ Descargando cursos desde Moodle...")
courses = call("core_course_get_courses")

parsed = []

for c in courses:
    ref = (
        extract_reference(c["shortname"]) or 
        extract_reference(c["fullname"])
    )

    parsed.append({
        "id": c["id"],
        "reference_code": ref,
        "fullname": c["fullname"],
        "shortname": c.get("shortname"),
        "summary": c.get("summary", "")
    })

with open("moodle_courses.yaml", "w", encoding="utf-8") as f:
    yaml.dump(parsed, f, allow_unicode=True, sort_keys=False)

print("✅ Archivo actualizado: moodle_courses.yaml")
