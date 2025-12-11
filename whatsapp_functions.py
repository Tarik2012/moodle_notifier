"""
===========================================================
 WHATSAPP CLOUD API - FUNCIONES DE REFERENCIA (APUNTES)
 Proyecto: Moodle WhatsApp Notifier
===========================================================

Este archivo contiene TODAS las funciones, ejemplos, notas
y scripts reales para usar WhatsApp Cloud API.

No es parte del proyecto Django — es un documento de referencia.
"""

import requests
import json

# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================

ACCESS_TOKEN = "AQUI_TU_TOKEN_REAL"
PHONE_NUMBER_ID = "AQUI_PHONE_NUMBER_ID"
API_VERSION = "v22.0"

# Construcción del endpoint principal:
BASE_URL = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}


# ==========================================================
# 1) FUNCIÓN BASE PARA ENVIAR MENSAJES
# ==========================================================
def send_whatsapp_request(payload):
    """
    Envía cualquier tipo de mensaje a WhatsApp usando un payload JSON.
    """
    response = requests.post(BASE_URL, headers=HEADERS, json=payload)

    try:
        return response.status_code, response.json()
    except:
        return response.status_code, {"error": "Invalid JSON", "raw": response.text}


# ==========================================================
# 2) ENVIAR UN MENSAJE DE PLANTILLA (sin parámetros)
# ==========================================================
def send_template_basic(to_number, template_name, language="en_US"):
    """
    Envía una plantilla simple SIN variables.
    """

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language}
        }
    }

    return send_whatsapp_request(payload)


# EJEMPLO REAL (usado por Tarek):
"""
ACCESS_TOKEN = "..." 
PHONE_NUMBER_ID = "956807774174705"
RECIPIENT = "34610970913"

send_template_basic(
    to_number="34610970913",
    template_name="jaspers_market_plain_text_v1"
)
"""


# ==========================================================
# 3) ENVIAR PLANTILLA CON PARÁMETROS (variables)
# ==========================================================
def send_template_with_params(to_number, template_name, params, language="en_US"):
    """
    Envía una plantilla que tiene variables, ej:
    Hola {{1}}, tu progreso es {{2}}%.
    """

    components = [
        {
            "type": "body",
            "parameters": [{"type": "text", "text": str(p)} for p in params]
        }
    ]

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
            "components": components
        }
    }

    return send_whatsapp_request(payload)


# ==========================================================
# 4) ENVIAR MENSAJE DE TEXTO NORMAL (non-template)
# IMPORTANTE: Solo funciona para números registrados como "test"
# ==========================================================
def send_text_message(to_number, text):
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    }
    return send_whatsapp_request(payload)

"""
NOTA:
Enviar mensajes NO BASADOS EN PLANTILLAS a usuarios normales NO ES POSIBLE,
solo a números verificados como "Test numbers".
"""


# ==========================================================
# 5) ERRORES COMUNES
# ==========================================================
ERRORS = {
    "470": "Template name invalid",
    "131047": "Template no aprobada",
    "131051": "El mensaje contiene parámetros incorrectos",
    "131000": "El mensaje no se puede enviar (usuario no disponible)",
    "10": "Acceso denegado por permisos",
}

"""
Ejemplo de error frecuente:

{'error': 
    {'message': '(#131047) No matching template.',
     'type': 'OAuthException',
     'code': 131047,
     'error_subcode': 2494010,
     'fbtrace_id': 'XYZ123'}
}

Esto significa:
❌ La plantilla NO existe
❌ O NO está aprobada
❌ O el nombre está mal escrito
"""


# ==========================================================
# 6) EJEMPLOS AVANZADOS (para el proyecto)
# ==========================================================

def send_welcome_message(to_number, student_name):
    return send_template_with_params(
        to_number,
        template_name="bienvenida_curso",
        params=[student_name]
    )


def send_progress_message(to_number, student_name, progress):
    return send_template_with_params(
        to_number,
        template_name="progreso_actualizado",
        params=[student_name, progress]
    )


def send_inactivity_message(to_number, student_name, days):
    return send_template_with_params(
        to_number,
        template_name="recordatorio_inactividad",
        params=[student_name, days]
    )


def send_completion_message(to_number, student_name):
    return send_template_with_params(
        to_number,
        template_name="curso_finalizado",
        params=[student_name]
    )

"""
Estas funciones se conectarán con nuestro sistema Django
cuando calculamos el progreso real del alumno.
"""

# ==========================================================
# 7) RESUMEN IMPORTANTE
# ==========================================================
"""
✔ SOLO se pueden enviar mensajes a usuarios REALES usando plantillas.
✔ Las plantillas DEBEN estar aprobadas por Meta.
✔ Todas las plantillas tienen un NOMBRE EXACTO.
✔ Los parámetros deben coincidir con las variables {{1}}, {{2}}, etc.
✔ Los mensajes sin plantilla se limitan a números de prueba.
✔ Para producción SIEMPRE usar plantillas personalizadas.

Plantillas que Tarek ya tiene listas:
- bienvenida_curso
- progreso_actualizado
- recordatorio_inactividad
- curso_finalizado
"""
