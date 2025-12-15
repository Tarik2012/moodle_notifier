from django.contrib import admin

from whatsapp_app.models import MessageLog


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ("id", "phone_number", "template_name", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("phone_number", "template_name")
