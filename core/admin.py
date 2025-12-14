from django.contrib import admin
from .models import (
    Course,
    Enrollment,
    ExternalSyncLog,
    MessageLog,
    ProgressSnapshot,
    Student,
)

admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(ProgressSnapshot)
admin.site.register(MessageLog)
admin.site.register(ExternalSyncLog)
