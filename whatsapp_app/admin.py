from django.contrib import admin

from whatsapp_app.models import MessageLog


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "template_name",
        "student",
        "course",
        "phone_number",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "template_name",
        "created_at",
    )

    search_fields = (
        "phone_number",
        "template_name",
        "student__first_name",
        "student__last_name",
        "course__name",
    )

    readonly_fields = (
        "created_at",
    )
