import requests
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Course


class Command(BaseCommand):
    help = "Sincroniza los cursos desde Moodle"

    # -----------------------------------------
    # Llamada genérica a Moodle
    # -----------------------------------------
    def call_moodle(self, func, params=None):
        base = {
            "wstoken": settings.MOODLE_TOKEN,
            "wsfunction": func,
            "moodlewsrestformat": "json",
        }
        if params:
            base.update(params)

        response = requests.get(settings.MOODLE_URL, params=base)
        return response.json()

    # -----------------------------------------
    # Extraer referencia tipo 159/03, 06802/01...
    # -----------------------------------------
    def extract_reference(self, text):
        if not text:
            return None
        match = re.search(r"\b\d{2,5}/\d{1,2}\b", text)
        return match.group(0) if match else None

    # -----------------------------------------
    # Handle → Ejecución del comando
    # -----------------------------------------
    def handle(self, *args, **options):
        self.stdout.write("⏳ Obteniendo cursos desde Moodle...")

        courses = self.call_moodle("core_course_get_courses")

        if isinstance(courses, dict) and courses.get("exception"):
            self.stdout.write(self.style.ERROR("❌ Error al obtener cursos"))
            self.stdout.write(str(courses))
            return

        self.stdout.write(self.style.SUCCESS(f"📘 Cursos recibidos: {len(courses)}"))

        saved = 0
        updated = 0

        for c in courses:
            reference = (
                self.extract_reference(c.get("shortname")) or
                self.extract_reference(c.get("fullname"))
            )

            obj, created = Course.objects.update_or_create(
                moodle_course_id=c["id"],
                defaults={
                    "reference_code": reference,
                    "name": c["fullname"],
                    "shortname": c.get("shortname"),
                    "description": c.get("summary", "")
                }
            )

            if created:
                saved += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Nuevos cursos guardados: {saved}"))
        self.stdout.write(self.style.SUCCESS(f"🔄 Cursos actualizados: {updated}"))
        self.stdout.write(self.style.SUCCESS("🎉 Sincronización completada"))
