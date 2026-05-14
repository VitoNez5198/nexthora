from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from .models import Service, BusinessHours, TimeOff, ProfessionalProfile
import datetime

# --- FORMULARIO DE REGISTRO ---
class NexthoraUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Requerido. Ingresa un email válido.")
    display_name = forms.CharField(
        max_length=100, 
        required=True, 
        help_text="El nombre de tu negocio o tu nombre profesional.",
        label="Nombre del Negocio"
    )
    slug = forms.CharField(
        max_length=100, 
        required=True, 
        help_text="Tu enlace personalizado. Ej: nexthora.com/tu-negocio",
        label="URL Personalizada"
    )
    whatsapp_number = forms.CharField(
        max_length=20, 
        required=True, 
        help_text="Número de WhatsApp (Ej: +56912345678)",
        label="WhatsApp del Negocio"
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email", "display_name", "slug", "whatsapp_number")

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            slug_formateado = slugify(slug)
            palabras_reservadas = ['admin', 'dashboard', 'login', 'register', 'logout', 'api', 'settings']
            if slug_formateado in palabras_reservadas:
                raise ValidationError("Esta URL no está disponible. Por favor, elige otra.")
            if ProfessionalProfile.objects.filter(slug=slug_formateado).exists():
                raise ValidationError("Este enlace ya está en uso por otro profesional.")
            return slug_formateado
        return slug

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save() # Guarda el usuario y dispara la señal que crea el ProfessionalProfile
            # Actualizamos el perfil recién creado
            profile = user.profile
            profile.display_name = self.cleaned_data["display_name"]
            profile.slug = self.cleaned_data["slug"]
            profile.whatsapp_number = self.cleaned_data["whatsapp_number"]
            
            # Limpiar WhatsApp para que empiece con +569 o similar
            clean_number = ''.join(filter(str.isdigit, profile.whatsapp_number))
            if len(clean_number) == 8:
                profile.whatsapp_number = f"+569{clean_number}"
            elif len(clean_number) == 9 and clean_number.startswith('9'):
                profile.whatsapp_number = f"+56{clean_number}"
                
            profile.save()
        return user

# --- FORMULARIO DE ACTUALIZACIÓN DE CUENTA ---
class AccountSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all'}),
        }
        labels = {
            'username': 'Nombre de Usuario',
            'email': 'Correo Electrónico',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este correo electrónico ya está en uso por otra cuenta.")
        return email

# --- FORMULARIO DE PERFIL PROFESIONAL ---
class ProfessionalProfileForm(forms.ModelForm):
    slug = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-r-xl border border-gray-200 bg-gray-50 text-gray-500 outline-none cursor-not-allowed select-none', 
            'placeholder': 'mi-negocio',
            'readonly': 'readonly'
        })
    )

    class Meta:
        model = ProfessionalProfile
        fields = ['profile_picture', 'banner_image', 'display_name', 'slug', 'bio', 'instagram_url', 'website_url', 'linkedin_url', 'facebook_url']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-bold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer'}),
            'banner_image': forms.FileInput(attrs={'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-bold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100 cursor-pointer'}),
            'display_name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all', 'placeholder': 'Ej: Alexander Thorne o Consultoría Thorne'}),
            'bio': forms.Textarea(attrs={'class': 'w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all resize-none', 'rows': 4, 'placeholder': 'Comparte tu experiencia, pasión y lo que los clientes pueden esperar...'}),
            'instagram_url': forms.URLInput(attrs={'class': 'w-full px-4 py-3 rounded-r-xl border border-gray-200 focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all', 'placeholder': 'https://instagram.com/tu_usuario'}),
            'website_url': forms.URLInput(attrs={'class': 'w-full px-4 py-3 rounded-r-xl border border-gray-200 focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all', 'placeholder': 'https://tusitio.com'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'w-full px-4 py-3 rounded-r-xl border border-gray-200 focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all', 'placeholder': 'https://linkedin.com/in/tu_perfil'}),
            'facebook_url': forms.URLInput(attrs={'class': 'w-full px-4 py-3 rounded-r-xl border border-gray-200 focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all', 'placeholder': 'https://facebook.com/tu_pagina'}),
        }
        labels = {
            'profile_picture': 'Foto de Perfil',
            'banner_image': 'Banner de Perfil (PRO)',
            'display_name': 'Nombre Completo / Nombre del Negocio',
            'slug': 'URL Personalizada',
            'bio': 'Sobre ti',
            'instagram_url': 'Perfil de Instagram',
            'website_url': 'Sitio Web / Portafolio',
            'linkedin_url': 'Perfil de LinkedIn',
            'facebook_url': 'Página de Facebook',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and getattr(self.instance, 'plan', 'FREE') != 'FREE':
            self.fields['slug'].widget.attrs.pop('readonly', None)
            self.fields['slug'].widget.attrs['class'] = 'w-full px-4 py-3 rounded-r-xl border border-gray-200 focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 outline-none transition-all text-gray-900 bg-white'

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            slug_formateado = slugify(slug)
            palabras_reservadas = ['admin', 'dashboard', 'login', 'register', 'logout', 'api', 'settings']
            if slug_formateado in palabras_reservadas:
                raise ValidationError("Esta URL no está disponible. Por favor, elige otra.")
            if ProfessionalProfile.objects.filter(slug=slug_formateado).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Este enlace ya está en uso por otro profesional.")
            return slug_formateado
        return slug

    def clean_profile_picture(self):
        foto = self.cleaned_data.get('profile_picture')
        if foto:
            limite_mb = 2
            if foto.size > limite_mb * 1024 * 1024:
                raise ValidationError(f"La imagen es muy pesada. El tamaño máximo permitido es {limite_mb}MB.")
            extensiones_validas = ['.jpg', '.jpeg', '.png', '.webp']
            if not any(foto.name.lower().endswith(ext) for ext in extensiones_validas):
                 raise ValidationError("Formato no válido. Sube una imagen en JPG, PNG o WEBP.")
        return foto

# --- FORMULARIO DE SERVICIOS ---
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
        # SOLUCIÓN: Añadimos la clase 'peer' aquí al lado de 'hidden'
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'hidden peer'}), 
        label="Días"
    )
    start_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-600 focus:border-blue-600 bg-white text-center font-mono cursor-pointer outline-none'}),
        label="Desde", initial="09:00"
    )
    end_time = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-600 focus:border-blue-600 bg-white text-center font-mono cursor-pointer outline-none'}),
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
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-600 focus:border-blue-600 outline-none'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-600 focus:border-blue-600 outline-none'}),
            'description': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-600 focus:border-blue-600 outline-none', 'placeholder': 'Ej: Vacaciones'}),
        }
        labels = { 'start_date': 'Desde', 'end_date': 'Hasta', 'description': 'Motivo' }
    
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")
        if start and end and start > end:
            raise forms.ValidationError("La fecha de fin no puede ser anterior al inicio.")
        return cleaned_data

# --- FORMULARIO DE CONFIGURACIÓN PRO ---
class ProScheduleSettingsForm(forms.ModelForm):
    class Meta:
        model = ProfessionalProfile
        fields = ['buffer_time_minutes', 'lunch_start_time', 'lunch_end_time']
        widgets = {
            'buffer_time_minutes': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-600 focus:border-blue-600 outline-none', 'min': 0, 'max': 120}),
            'lunch_start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-600 focus:border-blue-600 outline-none'}),
            'lunch_end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-600 focus:border-blue-600 outline-none'}),
        }
        labels = {
            'buffer_time_minutes': 'Descanso entre citas (min)',
            'lunch_start_time': 'Inicio de Colación',
            'lunch_end_time': 'Fin de Colación',
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("lunch_start_time")
        end = cleaned_data.get("lunch_end_time")
        if start and end and start >= end:
            raise forms.ValidationError("La hora de fin de colación debe ser después del inicio.")
        if (start and not end) or (end and not start):
            raise forms.ValidationError("Debes especificar tanto el inicio como el fin de la colación, o dejar ambos vacíos.")
        return cleaned_data