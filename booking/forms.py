from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Service, BusinessHours, TimeOff, ProfessionalProfile
import datetime

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

class ProfessionalProfileForm(forms.ModelForm):
    class Meta:
        model = ProfessionalProfile
        # Añadimos instagram_url y website_url
        fields = ['display_name', 'slug', 'bio', 'instagram_url', 'website_url']
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all', 'placeholder': 'Ej: Alexander Thorne o Consultoría Thorne'}),
            'slug': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-r-xl border border-gray-200 focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all', 'placeholder': 'mi-negocio'}),
            'bio': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all resize-none', 'rows': 4, 'placeholder': 'Comparte tu experiencia, pasión y lo que los clientes pueden esperar...'}),
            'instagram_url': forms.URLInput(attrs={'class': 'w-full px-4 py-3 rounded-r-xl border border-gray-200 focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all', 'placeholder': 'https://instagram.com/tu_usuario'}),
            'website_url': forms.URLInput(attrs={'class': 'w-full px-4 py-3 rounded-r-xl border border-gray-200 focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all', 'placeholder': 'https://tusitio.com'}),
        }
        labels = {
            'display_name': 'Nombre Completo / Nombre del Negocio',
            'slug': 'URL Personalizada',
            'bio': 'Sobre ti',
            'instagram_url': 'Perfil de Instagram',
            'website_url': 'Sitio Web / Portafolio',
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration_minutes', 'price', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-600 focus:border-blue-600 outline-none'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-600 focus:border-blue-600 outline-none', 'rows': 3}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-600 focus:border-blue-600 outline-none'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-600 focus:border-blue-600 outline-none'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-600 outline-none'}),
        }
        labels = {'name': 'Nombre del Servicio', 'description': 'Descripción (Opcional)', 'duration_minutes': 'Duración (minutos)', 'price': 'Precio (CLP)', 'is_active': 'Activo (Visible)',}

class BatchScheduleForm(forms.Form):
    WEEKDAYS = [(0, "Lu"), (1, "Ma"), (2, "Mi"), (3, "Ju"), (4, "Vi"), (5, "Sa"), (6, "Do")]
    TIME_CHOICES = [(f"{h:02}:{m:02}", f"{h:02}:{m:02}") for h in range(24) for m in (0, 30)]
    days = forms.MultipleChoiceField(choices=WEEKDAYS, widget=forms.CheckboxSelectMultiple(attrs={'class': 'hidden'}), label="Días")
    start_time = forms.ChoiceField(choices=TIME_CHOICES, widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-600 focus:border-blue-600 bg-white text-center font-mono cursor-pointer outline-none'}), label="Desde", initial="09:00")
    end_time = forms.ChoiceField(choices=TIME_CHOICES, widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-600 focus:border-blue-600 bg-white text-center font-mono cursor-pointer outline-none'}), label="Hasta", initial="18:00")
    def clean(self):
        cleaned_data = super().clean()
        if start_str := cleaned_data.get("start_time"):
            if end_str := cleaned_data.get("end_time"):
                start = datetime.datetime.strptime(start_str, "%H:%M").time()
                end = datetime.datetime.strptime(end_str, "%H:%M").time()
                if start >= end: raise forms.ValidationError("La hora de término debe ser después del inicio.")
                cleaned_data['start_time'] = start
                cleaned_data['end_time'] = end
        return cleaned_data

class TimeOffForm(forms.ModelForm):
    class Meta:
        model = TimeOff
        fields = ['start_date', 'end_date', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-600 focus:border-blue-600 outline-none'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-600 focus:border-blue-600 outline-none'}),
            'description': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-600 focus:border-blue-600 outline-none', 'placeholder': 'Ej: Vacaciones'}),
        }
        labels = { 'start_date': 'Desde', 'end_date': 'Hasta', 'description': 'Motivo' }
    def clean(self):
        cleaned_data = super().clean()
        if (start := cleaned_data.get("start_date")) and (end := cleaned_data.get("end_date")) and start > end:
            raise forms.ValidationError("La fecha de fin no puede ser anterior al inicio.")