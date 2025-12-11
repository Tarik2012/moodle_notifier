# ============================================================

# MOODLE WHATSAPP NOTIFIER — DOCUMENTACIÓN COMPLETA

# ============================================================

Versión: 1.0  
Autor: Tarek Errochdi  
Proyecto profesional para automatizar matrículas, seguimiento SCORM
y envío de mensajes por WhatsApp utilizando plantillas aprobadas.

---

# ============================================================

# 1. OBJETIVO GENERAL DEL SISTEMA

# ============================================================

Construir un sistema completo capaz de:

✔ Crear alumnos desde nuestra propia plataforma (Django)  
✔ Crear automáticamente esos alumnos en Moodle (API)  
✔ Matricularlos en cursos Moodle  
✔ Obtener el progreso REAL del alumno usando SCORM tracking  
✔ Guardar snapshots de progreso en PostgreSQL  
✔ Detectar inactividad, subida de progreso y finalización  
✔ Enviar mensajes automáticos por WhatsApp usando plantillas  
✔ Registrar todos los mensajes enviados  
✔ Mostrar todo en un panel interno

---

# ============================================================

# 2. ARQUITECTURA GENERAL DEL PROYECTO

# ============================================================

```
                ┌────────────────────────┐
                │    Django Backend       │
                │ (nuestra plataforma)    │
                └──────────┬─────────────┘
                           │
              ┌────────────┼────────────┐
              │             │            │
              ▼             ▼            ▼
       Student Module   Moodle API   WhatsApp API
       (Alta + Matricula) (SCORM WS)  (Plantillas)
```

Módulos Django:

- `core` → modelos base
- `moodle_app` → comunicación con Moodle
- `whatsapp_app` → comunicación con WhatsApp
- `notifier` → reglas y lógica
- `dashboard` → panel interno

---

# ============================================================

# 3. APUNTES OFICIALES MOODLE API (FUNCIONES + EJEMPLOS)

# ============================================================

```python
import requests

MOODLE_URL = "https://campus.formasuronline.es/webservice/rest/server.php"
TOKEN = "AQUI_TU_TOKEN"
BASE_PARAMS = {
    "wstoken": TOKEN,
    "moodlewsrestformat": "json",
}

def call(funcion, extra_params=None, method="GET"):
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
```

---

## ✔ Crear usuario Moodle

Devuelve **el ID** del usuario creado.

```python
def create_user(firstname, lastname, email, username, password, phone=None):
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
    return res[0]["id"]
```

---

## ✔ Matricular usuario:

```python
def enroll_user(user_id, course_id, role_id=5):
    params = {
        "enrolments[0][roleid]": role_id,
        "enrolments[0][userid]": user_id,
        "enrolments[0][courseid]": course_id,
    }
    return call("enrol_manual_enrol_users", params, method="POST")
```

---

## ✔ Obtener contenido del curso (para detectar SCORMs)

```python
def get_course_contents(course_id):
    return call("core_course_get_contents", {"courseid": course_id})
```

---

## ✔ Obtener SCOES y Tracks (progreso real SCORM)

```python
def get_scorm_scoes(scorm_id):
    return call("mod_scorm_get_scorm_scoes", {"scormid": scorm_id})

def get_scorm_track(user_id, sco_id):
    return call("mod_scorm_get_scorm_sco_tracks", {
        "userid": user_id,
        "scoid": sco_id
    })
```

---

## ✔ Calcular progreso SCORM

```python
def calculate_scorm_progress(scorm_id, user_id):
    scoes = get_scorm_scoes(scorm_id)
    sco_list = [s for s in scoes.get("scoes", [])
                if s.get("launch") and s.get("scormtype") == "sco"]

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

    return (completed / total * 100) if total > 0 else 0
```

---

# ============================================================

# 4. APUNTES OFICIALES WHATSAPP CLOUD API

# ============================================================

Endpoint base:

```
POST https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages
```

Headers:

```python
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}
```

---

## ✔ Enviar plantilla básica

```python
def send_template_basic(to, template_name):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en_US"}
        }
    }
    return requests.post(BASE_URL, headers=HEADERS, json=payload).json()
```

---

## ✔ Enviar plantilla con variables

```python
def send_template_with_params(to, template_name, params):
    components = [{
        "type": "body",
        "parameters": [{"type": "text", "text": str(p)} for p in params]
    }]
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en_US"},
            "components": components
        }
    }
    return requests.post(BASE_URL, headers=HEADERS, json=payload).json()
```

---

# ============================================================

# 5. DISEÑO DEL SISTEMA COMPLETO (FLUJOS)

# ============================================================

## ✔ FLUJO 1 — Crear alumno

(Sistema interno → Moodle → Whatsapp)

```
Empleado crea alumno
↓
Django → create_user()
↓
Moodle devuelve user_id
↓
Django guarda Student con moodle_user_id
↓
Django → enroll_user()
↓
Crear Enrollment en BD
↓
Enviar WhatsApp de bienvenida
↓
Registrar log de envío
```

---

## ✔ FLUJO 2 — Tracking SCORM

```
Scheduler ejecuta cada 30 min
↓
Obtener todas las matrículas
↓
Para cada Enrollment:
    Obtener SCORMs
    Obtener SCOES
    Obtener tracks
    Calcular progreso
↓
Guardar ProgressSnapshot en BD
```

---

## ✔ FLUJO 3 — Notificaciones automáticas

```
Si progreso nuevo → enviar plantilla de progreso
Si alumno inactivo → enviar plantilla de inactividad
Si curso completado → enviar plantilla de finalización
↓
Registrar cada envío en MessageLog
```

---

# ============================================================

# 6. MODELOS DEL SISTEMA (RESUMEN)

# ============================================================

### Student

- moodle_user_id
- fullname
- phone
- email

### Course

- moodle_course_id
- name

### Enrollment

- student_id
- course_id

### ProgressSnapshot

- overall_progress
- details_json

### MessageLog

- template
- sent_at
- whatsapp_message_id

---

# ============================================================

# 7. ERRORES FRECUENTES (Moodle + WhatsApp)

# ============================================================

### Moodle

❌ “No permission to view module”  
→ El rol del token no tiene permisos

❌ “Invalid parameter value”  
→ Parámetro mal escrito

---

### WhatsApp

❌ “(#131047) No matching template”  
→ Nombre de plantilla incorrecto o no aprobada

❌ “(#131000) WABA cannot send message”  
→ Usuario sin WhatsApp

❌ “Phone number not formatted correctly”  
→ Debe incluir prefijo

---

# ============================================================

# 8. RESUMEN FINAL DEL SISTEMA

# ============================================================

✔ Sistema profesional  
✔ Escalable  
✔ Documentado  
✔ Basado en Django + PostgreSQL  
✔ Integrado con Moodle API  
✔ Integrado con WhatsApp Cloud API  
✔ Automatización real  
✔ Logs y seguimiento  
✔ Preparado para producción

Este archivo sirve como **documentación oficial** del proyecto.
