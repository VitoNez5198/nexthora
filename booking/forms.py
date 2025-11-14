from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class NexthoraUserCreationForm(UserCreationForm):
    """
    Un formulario de creación de usuario personalizado que
    EXIGE el campo de correo electrónico (email).
    """
    email = forms.EmailField(required=True, help_text="Se requiere un correo válido.")

    class Meta(UserCreationForm.Meta):
        # Le decimos que se base en el modelo 'User'
        model = User
        # Le decimos qué campos mostrar (el email ya lo añadimos arriba)
        fields = ("username", "email")

    def save(self, commit=True):
        # Sobrescribimos la función 'save' para asegurar que el email se guarde
        user = super(NexthoraUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user