# Moodle WhatsApp Notifier

Sistema interno para automatizar notificaciones por WhatsApp a estudiantes de Moodle, usando Django, Celery, Redis y WhatsApp Cloud API.  
Diseñado para entornos empresariales con bajo/medio volumen, priorizando fiabilidad, deduplicación y trazabilidad.

---

## Objetivo del proyecto

- Gestionar alumnos y matrículas desde una app Django propia
- Integrarse con Moodle para:
  - Crear usuarios
  - Matricular alumnos en cursos
  - Calcular progreso (SCORM)
- Enviar mensajes automáticos por WhatsApp según reglas de negocio
- Evitar mensajes duplicados
- No bloquear la aplicación web
- Mantener un registro auditable de todos los envíos

---

## Arquitectura general

Django (web / dominio)  
│  
├── Celery (tareas asíncronas)  
│ ├── Orquestadores (batch)  
│ └── Tasks por matrícula (aislamiento de fallos)  
│  
├── Redis (broker de mensajes)  
│  
└── WhatsApp Cloud API (Meta)

---

## Principios de diseño

- Django es la fuente de verdad
- Moodle es un sistema externo secundario
- WhatsApp no tiene autoreintentos
- Un intento = un MessageLog
- Idempotencia basada en base de datos
- Fallos aislados por matrícula
- Proyecto interno (no SaaS público)

---

## Stack tecnológico

- Python 3.13
- Django 5.x
- PostgreSQL
- Celery
- Redis
- Docker (previsto para despliegue)
- WhatsApp Cloud API
- Moodle Web Services (REST)
- pytest + pytest-django

---

## Apps principales

- **core**  
  Modelos de negocio: Student, Course, Enrollment

- **moodle_app**  
  Integración con Moodle (usuarios, cursos, progreso SCORM)

- **whatsapp_app**  
  Envío de mensajes WhatsApp y registro de intentos (MessageLog)

---

## Reglas de mensajería

### 1️ Bienvenida

- Se ejecuta al crear la matrícula
- Usa `transaction.on_commit`
- Un mensaje por alumno y curso

### 2️ Progreso

- Progreso entre 1% y 99%
- Ventana de deduplicación configurable
- Deduplicación por:
  - student
  - course
  - template
  - estados `PENDING + SENT`

### 3️ Repaso

- Curso finaliza mañana
- Progreso ≥ 100%
- Un solo mensaje

### 4️ Finalización

- Curso finaliza hoy
- Progreso ≥ 100%
- Un solo mensaje

---

## MessageLog

Cada intento de envío genera un registro auditable con estado:

- PENDING
- SENT
- FAILED

Sirve como fuente de verdad, sistema de deduplicación y auditoría.

---

## Celery

- Workers ejecutan tareas asíncronas
- Tareas grandes divididas en dispatcher + task por matrícula
- Redis como broker
- Sin Celery Beat por ahora (decisión consciente)

---

## Testing

Tests críticos con pytest:

```bash
pytest
```

---

## Variables de entorno

```env
DJANGO_SETTINGS_MODULE=notifier_backend.settings
WHATSAPP_TOKEN=xxxxxxxx
WHATSAPP_PHONE_ID=xxxxxxxx
REDIS_URL=redis://localhost:6379/0
```

En producción:

- DEBUG=False
- ALLOWED_HOSTS configurado
- SECRET_KEY seguro

---

## Docker (visión)

Despliegue previsto en servidor de empresa con:

- Django
- Celery worker
- Redis
- PostgreSQL

El servidor está siempre encendido; el PC del desarrollador solo accede.

---

## Estado del proyecto

- Funcional
- Reglas críticas probadas
- Deduplicación implementada
- Riesgos conocidos y aceptados
- Listo para despliegue interno

---

## Próximos pasos

- Dockerización final
- Checklist de producción
- Monitorización básica
- Scheduling (cron / Celery Beat)
- Backups automáticos
