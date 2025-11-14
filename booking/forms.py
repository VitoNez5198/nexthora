from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class NexthoraUserCreationForm(UserCreationForm):
    """
    Un formulario de creación de usuario personalizado que
    exige el correo electrónico.
    """
    email = forms.EmailField(
        required=True, 
        help_text="Requerido. Por favor, introduce un correo electrónico válido."
    )

    class Meta(UserCreationForm.Meta):
        """
        Le dice a Django que use nuestro modelo de Usuario y que
        incluya los campos 'username', 'email', y las contraseñas.
        """
        model = User
        fields = ('username', 'email')

    def save(self, commit=True):
        """
        Guarda el usuario y se asegura de que el email
        se guarde correctamente.
        """
        user = super().save(commit=False)
        # Aseguramos que el email del formulario se asigne al modelo
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user