from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
import datetime

class ProfessionalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    slug = models.SlugField(max_length=100, unique=True, blank=True, help_text="La URL pública de tu perfil.")
    display_name = models.CharField(max_length=100, help_text="El nombre de tu negocio.")
    bio = models.TextField(max_length=500, blank=True, null=True, help_text="Describe brevemente tus servicios.")
    
    # --- NUEVO: FOTO DE PERFIL ---
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, help_text="Sube una foto de perfil cuadrada.")
    
    # --- CAMPOS REDES SOCIALES ---
    instagram_url = models.URLField(max_length=200, blank=True, null=True, help_text="Link a tu perfil de Instagram")
    website_url = models.URLField(max_length=200, blank=True, null=True, help_text="Link a tu sitio web o portafolio")
    linkedin_url = models.URLField(max_length=200, blank=True, null=True, help_text="Link a tu perfil de LinkedIn")
    facebook_url = models.URLField(max_length=200, blank=True, null=True, help_text="Link a tu página de Facebook")

    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.user.username) if self.user.username else "perfil"
            new_slug = base_slug
            counter = 1
            while ProfessionalProfile.objects.filter(slug=new_slug).exists():
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = new_slug
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        ProfessionalProfile.objects.create(user=instance)
    instance.profile.save()

class BusinessHours(models.Model):
    WEEKDAYS = [(0, "Lunes"), (1, "Martes"), (2, "Miércoles"), (3, "Jueves"), (4, "Viernes"), (5, "Sábado"), (6, "Domingo")]
    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE, related_name="business_hours")
    weekday = models.IntegerField(choices=WEEKDAYS, help_text="Día de la semana")
    start_time = models.TimeField(help_text="Hora de inicio")
    end_time = models.TimeField(help_text="Hora de fin")

    def __str__(self):
        return f"{self.professional.display_name} - {self.get_weekday_display()}: {self.start_time} a {self.end_time}"
    
    class Meta:
        ordering = ['weekday', 'start_time']
        unique_together = ('professional', 'weekday', 'start_time', 'end_time')

class Service(models.Model):
    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    duration_minutes = models.IntegerField(help_text="Duración total del servicio en minutos.")
    price = models.IntegerField(help_text="Precio a mostrar", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.professional.display_name})"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmada'),
        ('CANCELLED_BY_CLIENT', 'Cancelada por Cliente'),
        ('CANCELLED_BY_PRO', 'Cancelada por Profesional'),
        ('COMPLETED', 'Completada'),
    ]
    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.SET_NULL, null=True, related_name="appointments")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name="appointments")
    client_name = models.CharField(max_length=100, verbose_name="Nombre")
    client_last_name = models.CharField(max_length=100, verbose_name="Apellido", default="")
    client_rut = models.CharField(max_length=12, verbose_name="RUT", default="")
    client_email = models.EmailField(verbose_name="Email")
    client_whatsapp = models.CharField(max_length=20, verbose_name="WhatsApp", default="")
    
    start_datetime = models.DateTimeField(help_text="Fecha y hora de inicio de la cita")
    end_datetime = models.DateTimeField(help_text="Fecha y hora de fin de la cita")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cita: {self.client_name} {self.client_last_name} - {self.start_datetime}"

    def save(self, *args, **kwargs):
        if self.start_datetime and self.service:
            self.end_datetime = self.start_datetime + datetime.timedelta(minutes=self.service.duration_minutes)
        if self.client_whatsapp:
            clean_number = ''.join(filter(str.isdigit, self.client_whatsapp))
            if len(clean_number) == 8:
                self.client_whatsapp = f"+569{clean_number}"
            elif len(clean_number) == 9 and clean_number.startswith('9'):
                self.client_whatsapp = f"+56{clean_number}"
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['start_datetime']

class TimeOff(models.Model):
    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE, related_name="time_off")
    start_date = models.DateField(help_text="Fecha de inicio")
    end_date = models.DateField(help_text="Fecha de fin")
    description = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.professional} off: {self.start_date} - {self.end_date}"