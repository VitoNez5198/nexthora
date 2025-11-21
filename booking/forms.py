from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms  # <--- CAMBIO IMPORTANTE AQUÍ
from .models import Service
from .models import BusinessHours # Asegúrate de importar el modelo


class NexthoraUserCreationForm(UserCreationForm):
    """
    Un formulario personalizado para crear un usuario.
    Hereda TODO de UserCreationForm (incluida la validación de 
    contraseña, que usa un campo llamado 'password2').
    
    Nosotros solo le AÑADIMOS el campo 'email'.
    """
    # Ahora usamos forms.EmailField porque importamos 'django import forms'
    email = forms.EmailField(
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
        
class BusinessHoursForm(forms.ModelForm):
    class Meta:
        model = BusinessHours
        fields = ['weekday', 'start_time', 'end_time']
        widgets = {
            'weekday': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary'}),
        }
        labels = {
            'weekday': 'Día de la Semana',
            'start_time': 'Hora de Inicio',
            'end_time': 'Hora de Fin',
        }
    
    # Validación personalizada: Fin debe ser después de Inicio
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("La hora de fin debe ser posterior a la hora de inicio.")