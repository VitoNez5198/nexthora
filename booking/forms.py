from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import EmailField, forms
from .models import Service

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
    
    # ... (tu NexthoraUserCreationForm existente) ...


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary', 'rows': 3}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-primary border-gray-300 rounded focus:ring-primary'}),
        }
        labels = {
            'name': 'Nombre del Servicio',
            'description': 'Descripción (Opcional)',
            'duration_minutes': 'Duración (minutos)',
            'price': 'Precio (CLP)',
            'is_active': 'Activo (Visible para clientes)',
        }