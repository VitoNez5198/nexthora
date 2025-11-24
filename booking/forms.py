from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Service, BusinessHours, TimeOff
import datetime

# --- FORMULARIO DE REGISTRO ---
class NexthoraUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Requerido. Ingresa un email válido.")
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email",)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

# --- FORMULARIO DE SERVICIOS ---
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
            'is_active': 'Activo (Visible)',
        }

# --- FORMULARIO DE HORARIO POR LOTES ---
class BatchScheduleForm(forms.Form):
    WEEKDAYS = [(0, "Lu"), (1, "Ma"), (2, "Mi"), (3, "Ju"), (4, "Vi"), (5, "Sa"), (6, "Do")]
    TIME_CHOICES = []
    for h in range(24):
        for m in (0, 30):
            time_str = f"{h:02}:{m:02}"
            TIME_CHOICES.append((time_str, time_str))
    
    days = forms.MultipleChoiceField(
        choices=WEEKDAYS,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'hidden'}), 
        label="Días"
    )
    start_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary bg-white text-center font-mono cursor-pointer'}),
        label="Desde", initial="09:00"
    )
    end_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary bg-white text-center font-mono cursor-pointer'}),
        label="Hasta", initial="18:00"
    )

    def clean(self):
        cleaned_data = super().clean()
        start_str = cleaned_data.get("start_time")
        end_str = cleaned_data.get("end_time")
        if start_str and end_str:
            start = datetime.datetime.strptime(start_str, "%H:%M").time()
            end = datetime.datetime.strptime(end_str, "%H:%M").time()
            if start >= end:
                raise forms.ValidationError("La hora de término debe ser después del inicio.")
            cleaned_data['start_time'] = start
            cleaned_data['end_time'] = end
        return cleaned_data

# --- FORMULARIO DE DÍAS BLOQUEADOS ---
class TimeOffForm(forms.ModelForm):
    class Meta:
        model = TimeOff
        fields = ['start_date', 'end_date', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary'}),
            'description': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary', 'placeholder': 'Ej: Vacaciones'}),
        }
        labels = { 'start_date': 'Desde', 'end_date': 'Hasta', 'description': 'Motivo' }
    
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")
        if start and end and start > end:
            raise forms.ValidationError("La fecha de fin no puede ser anterior al inicio.")