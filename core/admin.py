from django.contrib import admin
from .models import Student, Course, Enrollment, ProgressSnapshot, MessageLog

admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(ProgressSnapshot)
admin.site.register(MessageLog)
