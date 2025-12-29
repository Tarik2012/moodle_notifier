# Moodle Notifier · Panel interno Formasur

Plataforma interna para:
- Gestión de alumnos y cursos Moodle
- Envío automático de mensajes WhatsApp
- Alertas médicas por caducidad de reconocimientos
- Paneles de control (Moodle + Salud Laboral)

Proyecto desarrollado en Django + Celery + Redis.
La ejecución periódica de alertas médicas se realiza mediante CRON (no Celery Beat).

---

## 1. Requisitos del sistema

Servidor Linux (Ubuntu recomendado)

Instalar previamente:
- Python 3.10+
- PostgreSQL
- Redis
- Git
- Cron (incluido por defecto en Linux)

---

## 2. Clonar el proyecto

git clone <REPOSITORIO_GITHUB>
cd moodle_notifier

---

## 3. Crear entorno virtual

python3 -m venv .venv
source .venv/bin/activate

---

## 4. Instalar dependencias

pip install -r requirements.txt

---

## 5. Variables de entorno (.env)

Crear un archivo .env en la raíz del proyecto:

DEBUG=False
SECRET_KEY=clave-secreta-segura
ALLOWED_HOSTS=127.0.0.1,localhost,IP_SERVIDOR

DATABASE_URL=postgres://usuario:password@localhost:5432/moodle_notifier

REDIS_URL=redis://127.0.0.1:6379/0

MOODLE_API_URL=https://moodle.dominio.com
MOODLE_API_TOKEN=token_moodle

WHATSAPP_TOKEN=token_whatsapp
WHATSAPP_PHONE_ID=id_telefono

---

## 6. Migraciones y usuario admin

python manage.py migrate
python manage.py createsuperuser

---

## 7. Arrancar servicios (modo producción interno)

### Django
python manage.py runserver 0.0.0.0:8000

### Redis
redis-server

### Celery Worker
celery -A notifier_backend worker -l info

---

## 8. Programación CRON (alertas médicas)

Las alertas médicas NO usan Celery Beat.
Se ejecutan una vez al día mediante CRON.

Editar cron:
crontab -e

Ejemplo (todos los días a las 08:00):

0 8 * * * /ruta/proyecto/.venv/bin/python /ruta/proyecto/manage.py send_medical_alerts >> /var/log/moodle_notifier_cron.log 2>&1

---

## 9. Acceso al sistema

- Panel principal: http://IP_SERVIDOR:8000/
- Admin Django: http://IP_SERVIDOR:8000/admin/

---

## 10. Notas importantes

- El proyecto está preparado para despliegue interno.
- Dockerización pendiente (opcional).
- No usar Celery Beat.
- Redis y Celery deben permanecer activos.
- CRON es obligatorio para alertas médicas.

---

Proyecto listo para uso interno en empresa.
