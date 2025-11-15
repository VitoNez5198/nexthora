from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import EmailField, forms

class NexthoraUserCreationForm(UserCreationForm):
    """
    Un formulario personalizado para crear un usuario.
    Hereda TODO de UserCreationForm (incluida la validación de 
    contraseña, que usa un campo llamado 'password2').
    
    Nosotros solo le AÑADIMOS el campo 'email'.
    """
    email = EmailField(
        required=True, 
        help_text="Requerido. Ingresa un email válido."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Le decimos que use los campos del padre, MÁS el email.
        fields = UserCreationForm.Meta.fields + ("email",)

    def save(self, commit=True):
        # Sobrescribimos el 'save' para asegurar que el email se guarde
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user