from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("whatsapp_app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="messagelog",
            name="response_payload",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="messagelog",
            name="status_code",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
