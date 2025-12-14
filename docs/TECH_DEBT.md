# Deudas tecnicas
- Apps dashboard, notifier, whatsapp_app y moodle_app mantienen vistas/modelos/tests como stubs (TODOs marcados); decidir si se implementan o se archivan.
- Scripts manuales `test/test_get_courses.py`, `test/export_courses_yaml.py` y `test_progress.py` conservan tokens de Moodle y no forman parte del runtime.
- Clientes Moodle duplicados (`moodle_app/api.py` y `moodle_app/moodle_client.py`) mas archivo de referencia `moodle_functions.py`; falta consolidacion o documentar el responsable unico.
- No hay pruebas para Celery (update_all_enrollments_progress) ni para flujos de WhatsApp; cobertura actual se limita a estudiantes.

# Riesgos conocidos
- `DEBUG` por defecto en True y `ALLOWED_HOSTS` abierto a "*"; riesgo en despliegues no locales.
- `SECRET_KEY` usa valor de desarrollo si falta en el entorno.
- Tokens expuestos en scripts de pruebas manuales bajo `test/` y en `test_progress.py`; requieren rotacion o aislamiento.
- Configuracion de base de datos apunta a Postgres via variables de entorno; sin override las pruebas pueden fallar si no hay servicio.

# Mejoras futuras sugeridas
- Consolidar un unico cliente Moodle y centralizar el manejo de errores/auditoria.
- Extraer scripts manuales a documentacion sin credenciales reales o parametrizarlos con variables de entorno.
- Completar o retirar los stubs de apps secundarias y registrar modelos en admin cuando existan.
- Ampliar pruebas a sincronizacion con Moodle/WhatsApp y a tareas Celery sin alterar los flujos actuales.
