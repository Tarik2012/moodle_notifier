# core/forms.py
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
        base_classes = (
            "w-full rounded-lg border border-gray-300 bg-white px-3 py-2 "
            "text-sm text-gray-900 placeholder:text-gray-400 "
            "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 "
            "transition"
        )
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {base_classes}".strip()
