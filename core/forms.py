from django import forms
from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "city",
            "address",
            "company",
            "dni",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # SOLO al crear alumno
        if not self.instance or not self.instance.pk:
            self.fields["password"] = forms.CharField(
                label="Contraseña Moodle",
                required=True,
                min_length=8,
                widget=forms.PasswordInput(),
                help_text="Mínimo 8 caracteres. No se guarda en la BD.",
            )

            self.fields["password_confirm"] = forms.CharField(
                label="Confirmar contraseña",
                required=True,
                widget=forms.PasswordInput(),
            )

        base_classes = (
            "w-full rounded-lg border border-gray-300 bg-white px-3 py-2 "
            "text-sm text-gray-900 placeholder:text-gray-400 "
            "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 "
            "transition"
        )

        for field in self.fields.values():
            field.widget.attrs["class"] = base_classes

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Las contraseñas no coinciden.")

        return cleaned_data
