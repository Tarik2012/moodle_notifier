from django.db import models


# =====================================================
# STUDENT
# =====================================================
class Student(models.Model):
    # ID del usuario en Moodle
    moodle_user_id = models.IntegerField(unique=True, null=True, blank=True)

    # Datos esenciales
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=30)

    # Datos opcionales
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    dni = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def course_count(self):
        # If the queryset annotated this instance, use the prefetched value
        if hasattr(self, "_course_count"):
            return self._course_count
        # Fallback to counting related enrollments
        return self.enrollments.count()

    @course_count.setter
    def course_count(self, value):
        # Allow annotations to set this attribute without raising
        self._course_count = value



# =====================================================
# COURSE
# =====================================================
class Course(models.Model):
    moodle_course_id = models.IntegerField(unique=True)

    # Código de referencia: 159/03, 174/02, 119/01, etc.
    reference_code = models.CharField(max_length=50, blank=True, null=True)

    name = models.CharField(max_length=255)
    shortname = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.reference_code} - {self.name}"



# =====================================================
# ENROLLMENT
# =====================================================
class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    progress = models.FloatField(default=0.0)   # <────── NUEVO

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} → {self.course}"



# =====================================================
# PROGRESS SNAPSHOT (Historial del progreso)
# =====================================================
class ProgressSnapshot(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    overall_progress = models.FloatField(default=0.0)
    details_json = models.JSONField(default=dict)

    snapshot_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.course}: {self.overall_progress}%"


# =====================================================
# MENSAJES ENVIADOS (WhatsApp Log)
# =====================================================
class MessageLog(models.Model):

    TEMPLATE_CHOICES = [
        ('welcome', 'Welcome'),
        ('progress', 'Progress'),
        ('inactivity', 'Inactivity'),
        ('completion', 'Completion'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)

    template_name = models.CharField(max_length=50, choices=TEMPLATE_CHOICES)
    sent_at = models.DateTimeField(auto_now_add=True)

    # ID real del mensaje enviado por WhatsApp Cloud API
    whatsapp_message_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.template_name} → {self.student} at {self.sent_at}"


# =====================================================
# EXTERNAL SYNC LOG (Moodle, etc.)
# =====================================================
class ExternalSyncLog(models.Model):
    service = models.CharField(max_length=50)
    action = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=100)
    entity_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service} - {self.action} - {self.status}"
